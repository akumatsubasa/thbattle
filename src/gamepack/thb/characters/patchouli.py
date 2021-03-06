# -*- coding: utf-8 -*-
from game.autoenv import EventHandler, Game
from .baseclasses import Character, register_character
from ..actions import DrawCards, ForEach, GenericAction, LaunchCard
from ..cards import Card, Skill, RejectCard, InstantSpellCardAction, Reject, SpellCardAction, t_None


class Library(Skill):
    associated_action = None
    target = t_None


class Knowledge(Skill):
    associated_action = None
    target = t_None


class LibraryDrawCards(DrawCards):
    pass


class KnowledgeAction(GenericAction):
    def __init__(self, act):
        self.source = self.target = act.target
        self.action = act

    def apply_action(self):
        self.action.cancelled = True
        return True


class PatchouliHandler(EventHandler):
    execute_before = ('RejectHandler', )

    def handle(self, evt_type, act):
        if evt_type == 'action_before':

            if isinstance(act, SpellCardAction) and not act.cancelled:
                tgt = act.target
                if tgt.has_skill(Knowledge):
                    c = getattr(act, 'associated_card', None)
                    if c and c.suit == Card.SPADE and not c.is_card(RejectCard):
                        Game.getgame().process_action(KnowledgeAction(act))

            try:
                src = act.source
            except AttributeError:
                return act

            if not src or not src.has_skill(Library): return act

            if isinstance(act, Reject):
                Game.getgame().process_action(LibraryDrawCards(src, 1))
                return act

            if isinstance(act, LaunchCard):
                aact = act.card.associated_action
                if issubclass(aact, InstantSpellCardAction):
                    Game.getgame().process_action(LibraryDrawCards(src, 1))
                    return act

                if issubclass(aact, ForEach) and issubclass(aact.action_cls, InstantSpellCardAction):
                    Game.getgame().process_action(LibraryDrawCards(src, 1))
                    return act

        return act


@register_character
class Patchouli(Character):
    skills = [Library, Knowledge]
    eventhandlers_required = [PatchouliHandler]
    maxlife = 3
