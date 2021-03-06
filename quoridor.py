#!/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
from pygame.locals import *
from pygame import Color
import threading
import argparse

from helpers import log, LogLevel
import config as cfg
import core

from entities.board import Board


def dispatch(events, board: Board):
    for event in events:
        if event.type == QUIT:
            return False

        if hasattr(event, 'key'):
            if event.key == K_ESCAPE or board.finished:
                return False

        if board.computing or board.finished:
            continue

        if event.type == MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            board.onMouseClick(x, y)

        if event.type == MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            board.onMouseMotion(x, y)

    return True


def main() -> int:
    core.init()

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--level",
                        help="AI player Level. Default is 0 (Easy). Higher is harder)",
                        default=cfg.LEVEL, type=int)

    parser.add_argument('-d', '--debug',
                        help="Debug mode", action='store_true')

    parser.add_argument('-C', '--cache',
                        help="Enable persistent memoize cache", action='store_true')

    options = parser.parse_args()
    cfg.LEVEL = options.level
    cfg.__DEBUG__ = options.debug
    cfg.CACHE_ENABLED = options.cache

    log('Quoridor AI game')
    #log('This program is Free')
    log('Initializing system...')

    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_mode((800, 600))
    pygame.display.set_caption(cfg.GAME_TITLE)
    screen = pygame.display.get_surface()

    screen.fill(Color(255, 255, 255))
    board = core.BOARD = Board(screen)
    board.draw()
    log('System initialized OK')

    if cfg.CACHE_ENABLED:
        if not os.path.exists(cfg.CACHE_DIR):
            log('Cache directory {} not found. Creating it...'.format(cfg.CACHE_DIR))
            os.makedirs(cfg.CACHE_DIR, exist_ok=True)

        if not os.path.isdir(cfg.CACHE_DIR):
            log('Could not create cache directory {}. Caching disabled'.format(cfg.CACHE_DIR), LogLevel.ERROR)
            cfg.CACHE_ENABLED = False

    cont = True
    if input("play with ex or ai?(y for ex)") == "y":
        cont1 = True
    else:
        cont1 = False
    while cont:
        clock.tick(cfg.FRAMERATE)
        pygame.display.flip()
        if cont1 == False:
            if not board.computing and not board.finished:
                if board.current_player.AI:
                    print("if not compute")
                    board.computing = True
                    thread = threading.Thread(target=board.computer_move)
                    thread.start()

        cont = dispatch(pygame.event.get(), board)
        cont1 = dispatch(pygame.event.get(), board)

    del board.rows

    pygame.quit()

    if cfg.CACHE_ENABLED:
        for pawn in board.pawns:
            if pawn.AI is not None:
                pawn.AI.flush_cache()

    log('Memoized nodes: %i' % core.MEMOIZED_NODES)
    log('Memoized nodes hits: %i' % core.MEMOIZED_NODES_HITS)

    for pawn in board.pawns:
        log('Memoized distances for [%i]: %i' % (pawn.id, pawn.distances.MEMO_COUNT))
        log('Memoized distances hits for [%i]: %i' % (pawn.id, pawn.distances.MEMO_HITS))

    log('Exiting. Bye!')
    return 0


if __name__ == '__main__':
    main()
