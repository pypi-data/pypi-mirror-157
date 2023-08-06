import asyncio
from typing import *

import wizwalker
from wizwalker.combat import CombatHandler
from wizwalker.combat import CombatMember
from wizwalker.combat.card import CombatCard
from wizwalker.memory import EffectTarget, SpellEffects

from .combat_backends.combat_config_parser import TargetType, TargetData, MoveConfig, TemplateSpell \
    , NamedSpell, SpellType, Spell
from .combat_backends.backend_base import BaseCombatBackend


class SprintyCombat(CombatHandler):
    def __init__(self, client: wizwalker.client.Client, config_provider: BaseCombatBackend):
        super().__init__(client)
        self.client: wizwalker.client.Client = client # to restore autocomplete
        self.config = config_provider
        self.turn_adjust = 0
        self.cur_card_count = 0
        self.prev_card_count = 0
        self.was_pass = False
        self.had_first_round = False
        self.rel_round_offset = 0

    async def handle_combat(self):
        self.turn_adjust = 0
        self.cur_card_count = 0
        self.prev_card_count = 0
        self.rel_round_offset = 0
        self.was_pass = False
        self.had_first_round = False
        await super().handle_combat()

    async def get_member_named(self, name: str) -> Optional[CombatMember]:
        # Issue: #4
        async def _inner():
            members: List[CombatMember] = await self.get_members()

            for member in members:
                if name == await member.name():
                    return member
            return None
        try:
            return await wizwalker.utils.maybe_wait_for_value_with_timeout(
                _inner,
                timeout=2.0
            )
        except wizwalker.errors.ExceptionalTimeout:
            return None

    async def get_member_vaguely_named(self, name: str) -> Optional[CombatMember]:
        # Issue #4
        async def _inner():
            members = await self.get_members()

            for member in members:
                if name.lower() in (await member.name()).lower():
                    return member
            return None
        try:
            return await wizwalker.utils.maybe_wait_for_value_with_timeout(
                _inner,
                timeout=2.0
            )
        except wizwalker.errors.ExceptionalTimeout:
            return None

    async def pass_button(self):
        self.was_pass = True
        await super().pass_button()

    async def get_cards(self) -> List[CombatCard]:  # extended to sort by enchanted
        async def _inner() -> List[CombatCard]:
            cards = await super(SprintyCombat, self).get_cards()
            rese, res = [], []
            for card in cards:
                if await card.is_enchanted():
                    rese.append(card)
                else:
                    res.append(card)
            return rese + res
        try:
            return await wizwalker.utils.maybe_wait_for_any_value_with_timeout(_inner, sleep_time=0.2, timeout=2.0)
        except wizwalker.errors.ExceptionalTimeout:
            return []

    async def get_card_named(self, name: str) -> Optional[CombatCard]:
        try:
            return await super().get_card_named(name)
        except ValueError:
            return None

    async def get_card_with_predicate(self, pred: Callable) -> Optional[CombatCard]:
        cards = await self.get_cards_with_predicate(pred)
        if len(cards) > 0:
            return cards[0]
        return None

    async def get_card_vaguely_named(self, name: str) -> Optional[CombatCard]:
        async def _pred(card: CombatCard):
            return name.lower() in (await card.name()).lower()

        return await self.get_card_with_predicate(_pred)

    async def get_card_counts(self) -> Tuple[int, int]:
        # Issue: #6. Very rare error
        async def _inner():
            window = None
            while window is None:
                window, *_ = await self.client.root_window.get_windows_with_name("CountText")
            text: str = await window.maybe_text()
            _, count_text = text.splitlines()
            count_text = count_text[8:-9]
            count_text = count_text.replace("of", "").strip()  # I know this sucks
            res1, res2 = count_text.split()
            return int(res1), int(res2)
        try:
            return await wizwalker.utils.maybe_wait_for_any_value_with_timeout(_inner, sleep_time=0.2, timeout=2.0)
        except wizwalker.errors.ExceptionalTimeout:
            return (0, 0) # TODO: Maybe propagate, but good enough for now

    async def get_castable_cards(self) -> List[CombatCard]:  # extension for castable cards only
        async def _pred(card: CombatCard):
            return await card.is_castable()

        return await self.get_cards_with_predicate(_pred)

    async def get_castable_cards_named(self, name: str) -> List[CombatCard]:
        cards = await self.get_castable_cards()
        res = []

        for card in cards:
            if name == await card.name():
                res.append(card)

        return res

    async def get_castable_cards_vaguely_named(self, name: str) -> List[CombatCard]:
        cards = await self.get_castable_cards()
        res = []
        for card in cards:
            if name.lower() in (await card.name()).lower():
                res.append(card)

        return res

    async def get_castable_card_named(self, name: str, only_enchants=False) -> Optional[CombatCard]:  # extension to get only castable card
        cards = await self.get_castable_cards()

        for card in cards:
            if name == await card.name():
                if only_enchants:
                    for e in await card.get_spell_effects():
                        if await e.effect_target() is EffectTarget.spell:
                            return card
                    else:
                        continue
                return card

        return None

    async def get_castable_card_vaguely_named(self, name: str, only_enchants=False) -> Optional[CombatCard]:
        cards = await self.get_castable_cards()

        for card in cards:
            if name.lower() in (await card.name()).lower():
                if only_enchants:
                    for e in await card.get_spell_effects():
                        if await e.effect_target() is EffectTarget.spell:
                            return card
                    else:
                        continue
                return card

        return None

    async def get_castable_enchanted_card_named(self, name: str) -> Optional[CombatCard]:
        for s in await self.get_castable_cards_named(name):
            if await s.is_enchanted():
                return s
        return None

    async def get_castable_enchanted_card_vaguely_named(self, name: str) -> Optional[CombatCard]:
        for s in await self.get_castable_cards_vaguely_named(name):
            if await s.is_enchanted():
                return s
        return None

    async def get_cards_by_template(self, template: TemplateSpell) -> list[CombatCard]:
        cards = await self.get_castable_cards()
        res = []
        allow_aoe = SpellType.type_aoe in template.requirements
        for c in cards:
            fits = True
            effects = await c.get_spell_effects()
            c_type = (await c.type_name()).lower()
            for req in template.requirements:
                if req is SpellType.type_damage:
                    for e in effects:
                        target = await e.effect_target()
                        eff = await e.effect_type()
                        if target in (EffectTarget.enemy_team,
                                      EffectTarget.enemy_team_all_at_once,
                                      EffectTarget.enemy_single) \
                                and eff in (SpellEffects.damage,
                                            SpellEffects.damage_over_time,
                                            SpellEffects.damage_per_total_pip_power) \
                                or c_type == "damage":
                            if target in (EffectTarget.enemy_team, EffectTarget.enemy_team_all_at_once) and allow_aoe:
                                break
                            elif target in (EffectTarget.enemy_team, EffectTarget.enemy_team_all_at_once):
                                continue
                            else:
                                break
                    else:
                        fits = False
                elif req is SpellType.type_aoe:
                    for e in effects:
                        target = await e.effect_target()
                        if target in (EffectTarget.enemy_team, EffectTarget.enemy_team_all_at_once,
                                      EffectTarget.friendly_team, EffectTarget.friendly_team_all_at_once):
                            break
                    else:
                        fits = False
                elif req is SpellType.type_trap:
                    for e in effects:
                        target = await e.effect_target()
                        et = await e.effect_type()
                        if et is SpellEffects.modify_incoming_damage and target is EffectTarget.enemy_single:
                            break
                    else:
                        fits = False
                elif req is SpellType.type_shield:
                    for e in effects:
                        target = await e.effect_target()
                        et = await e.effect_type()
                        if et is SpellEffects.modify_incoming_damage and target is EffectTarget.friendly_single:
                            break
                    else:
                        fits = False
                elif req is SpellType.type_blade:
                    for e in effects:
                        target = await e.effect_target()
                        et = await e.effect_type()
                        if et is SpellEffects.modify_incoming_damage and target is EffectTarget.friendly_single:
                            break
                    else:
                        fits = False
                elif req is SpellType.type_heal:
                    for e in await c.get_spell_effects():
                        if (await e.effect_type()) is SpellEffects.heal:
                            break
                    else:
                        fits = False
                elif req is SpellType.type_heal_other:
                    for e in effects:
                        target = await e.effect_target()
                        if (target is EffectTarget.friendly_team or target is EffectTarget.friendly_single) and (
                                await e.effect_type()) is SpellEffects.heal:
                            break
                    else:
                        fits = False
                elif req is SpellType.type_heal_self:
                    for e in effects:
                        target = await e.effect_target()
                        if (target is EffectTarget.self or target is EffectTarget.friendly_team) and (
                                await e.effect_type()) is SpellEffects.heal:
                            break
                    else:
                        fits = False
                elif req is SpellType.type_enchant:
                    for e in effects:
                        if await e.effect_target() is EffectTarget.spell:
                            break
                    else:
                        fits = False

                if not fits:
                    break
            if fits:
                res.append(c)
        return res

    async def get_boss_or_none(self) -> Optional[CombatMember]:
        for m in await self.get_members():
            if await m.is_boss():
                return m
        return None

    async def get_allies(self) -> List[CombatMember]:
        members = []
        my_client = await self.get_client_member()
        my_participant = await my_client.get_participant()
        my_team_id = await my_participant.team_id()
        my_id = await my_participant.owner_id_full()
        for mem in await self.get_members():
            participant = await mem.get_participant()
            if await participant.team_id() == my_team_id \
                    and await participant.owner_id_full() != my_id:
                members.append(mem)
        return members

    async def get_enemies(self) -> List[CombatMember]:
        members = []
        my_client = await self.get_client_member()
        my_participant = await my_client.get_participant()
        my_team_id = await my_participant.team_id()
        for mem in await self.get_members():
            participant = await mem.get_participant()
            if await participant.team_id() != my_team_id:
                members.append(mem)
        return members

    async def get_nth_ally_or_none(self, n: int) -> Optional[CombatMember]:
        allies = await self.get_allies()
        if len(allies) <= n:
            return None
        return allies[n]

    async def get_nth_enemy_or_none(self, n: int) -> Optional[CombatMember]:
        enemies = await self.get_enemies()
        if len(enemies) <= n:
            return None
        return enemies[n]

    async def try_get_config_target(self, target: TargetData) -> Union[bool, Optional[CombatMember]]:
        ttype = None
        data = None
        if target is not None:
            ttype = target.target_type
            data = target.extra_data
        else:
            return None

        if ttype is TargetType.type_boss:
            if boss := await self.get_boss_or_none():
                return boss
        elif ttype is TargetType.type_self:
            return await self.get_client_member()
        elif ttype is TargetType.type_aoe:
            return None
        elif ttype is TargetType.type_enemy:
            if data is None:
                if enemy := await self.get_nth_enemy_or_none(0):
                    return enemy
            else:
                if enemy := await self.get_nth_enemy_or_none(data):
                    return enemy
        elif ttype is TargetType.type_ally:
            if data is None:
                if ally := await self.get_nth_ally_or_none(0):
                    return ally
            else:
                if ally := await self.get_nth_ally_or_none(data):
                    return ally
        elif ttype is TargetType.type_named:
            if target.is_literal:
                if res := await self.get_member_named(data):
                    return res
            if res := await self.get_member_vaguely_named(data):
                return res

        return False

    async def try_get_spell(self, spell: Spell, only_enchants=False) -> Union[CombatCard, str, None]:
        if isinstance(spell, NamedSpell):
            spell: NamedSpell
            if spell.name in ("pass", "none"):
                return spell.name
            if spell.is_literal:
                return await self.get_castable_card_named(spell.name, only_enchants)
            else:
                return await self.get_castable_card_vaguely_named(spell.name, only_enchants)
        elif isinstance(spell, TemplateSpell):
            spell: TemplateSpell
            res = await self.get_cards_by_template(spell)
            if len(res) > 0:
                return res[0]
            return None
        else:
            raise NotImplementedError("Unknown spell config type")

    async def try_execute_config(self, move_config: MoveConfig) -> bool:
        cur_card = await self.try_get_spell(move_config.move.card)
        if cur_card is None:
            return False

        if cur_card == "pass":
            await self.pass_button()
            return True

        target = await self.try_get_config_target(move_config.target)

        if target == False:  # Wouldn't want a None to mess it up
            return False

        if move_config.move.enchant is not None and not await cur_card.is_enchanted():
            enchant_card = await self.try_get_spell(move_config.move.enchant, only_enchants=True)
            if enchant_card != "none":
                if enchant_card is not None:
                    # Issue: 5. Casting wasn't that reliable
                    pre_enchant_count = len(await self.get_cards())
                    while len(await self.get_cards()) == pre_enchant_count:
                        await enchant_card.cast(cur_card, sleep_time=self.config.cast_time*2)
                        await asyncio.sleep(self.config.cast_time*2) # give it some time for card list to update

                    self.cur_card_count -= 1

                elif enchant_card is None and (isinstance(move_config.move.enchant, TemplateSpell) and not move_config.move.enchant.optional):
                    return False

        to_cast = await self.try_get_spell(move_config.move.card)
        if to_cast is None:
            return False  # this should not happen
        
        # Issue: 5. Casting wasn't that reliable
        try:
            while to_cast != None:
                try: 
                    await to_cast.cast(target, sleep_time=self.config.cast_time)
                    await asyncio.sleep(self.config.cast_time) # give it some time for card list to update
                    to_cast = await self.try_get_spell(move_config.move.card)
                except ValueError:
                    break # Issue: 8
        except wizwalker.errors.WizWalkerMemoryError or ValueError:
            pass # Let it happen if it happens
        return True

    async def fail_turn(self):
        self.turn_adjust -= 1
        await self.pass_button()

    async def on_fizzle(self):
        self.turn_adjust -= 1

    async def handle_round(self):
        try:
            await self.client.mouse_handler.activate_mouseless()
        except wizwalker.errors.HookAlreadyActivated:
            pass
        
        try:
            self.config.attach_combat(self) # For safety. Could probably also do this in handle_combat

            real_round = await self.round_number()
            self.cur_card_count = len(await self.get_cards()) + (await self.get_card_counts())[0]

            if not self.had_first_round:
                current_round = real_round - 1
                if current_round > 0:
                    self.turn_adjust -= current_round
            else:
                if self.cur_card_count >= self.prev_card_count and not self.was_pass:
                    await self.on_fizzle()

            self.was_pass = False
            current_round = (real_round - 1 + self.turn_adjust + self.rel_round_offset)

            # Issue: #3. Need to make sure it's valid
            member: CombatMember = None
            try:
                member = await wizwalker.utils.maybe_wait_for_any_value_with_timeout(
                    self.get_client_member,
                    timeout=2.0
                )
            except wizwalker.errors.ExceptionalTimeout:
                # TODO: Maybe make this more dramatic
                await self.fail_turn() # This is quite catastrophic. Use default fail for now
            
            if member is not None:
                if await member.is_stunned():
                    await self.fail_turn()
                else:
                    round_config = await self.config.get_real_round(real_round)
                    if round_config is None:
                        round_config = await self.config.get_relative_round(current_round)
                    else:
                        self.rel_round_offset -= 1

                    if round_config is not None:
                        for p in round_config.priorities:  # go through rounds priorities
                            if await self.try_execute_config(p):
                                break  # we found a working priority and managed to cast it
                        else:
                            await self.pass_button()
                    else:  # Very bad. Probably using empty config
                        await self.config.handle_no_cards_given()

            self.had_first_round = True  # might go bad on throw
            self.prev_card_count = self.cur_card_count
        finally:
            try:
                await self.client.mouse_handler.deactivate_mouseless()
            except wizwalker.errors.HookNotActive:
                pass
