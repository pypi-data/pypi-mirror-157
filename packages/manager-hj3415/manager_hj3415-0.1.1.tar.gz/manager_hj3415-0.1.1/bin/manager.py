import os
import sys
import re
import argparse
import pprint
import pandas as pd
import datetime

from krx_hj3415 import krx
from util_hj3415 import noti
from eval_hj3415 import report, eval
from manager_hj3415.manager import sync_mongo_with_krx, make_refresh_targets

from scraper_hj3415.miscrapy import scraper as scraper_mi
from scraper_hj3415.nfscrapy import scraper as scraper_nfs

from db_hj3415 import dbpath, mongo2
from dart_hj3415 import opendart, analysis


import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


present_addr = dbpath.load()
try:
    client = mongo2.connect_mongo(present_addr)
except:
    pass
spiders = ['c101', 'c106', 'c108', 'c103', 'c104']


def set_scraper_subcommand(parents_parser):
    """
    parents_parser - subparsers
    """
    scraper_cmd = spiders + ['mi', 'mi_hx', 'gm']
    # create the parser for the "scraper" command
    scraper_parser = parents_parser.add_parser(
        'scraper',
        description=f"Scraper nf, mi, gm",
        help='Scraper nf, mi, gm',
        epilog=f"Present addr - {present_addr}",
    )
    scraper_parser.add_argument('scraper_cmd', choices=scraper_cmd)
    scraper_parser.add_argument('-m', '--message', action='store_true', help='Send telegram message with result after work.')
    spiders_group = scraper_parser.add_mutually_exclusive_group()
    spiders_group.add_argument('-c', '--code', metavar='code', help='Scrape one code')
    spiders_group.add_argument('-a', '--all', action='store_true', help='Scrape all codes')


def set_refresh_subcommand(parents_parser):
    """
    parents_parser - subparsers
    """
    refresh_cmd = ['run', 'set_count']
    # create the parser for the "refresh" command
    refresh_parser = parents_parser.add_parser(
        'refresh',
        description=f"Refreshing codes periodically",
        help='Refreshing codes periodically',
        epilog=f"Present addr - {present_addr}",
    )
    refresh_parser.add_argument('refresh_cmd', choices=refresh_cmd)
    refresh_parser.add_argument('-m', '--message', action='store_true', help='Send telegram message with result after work.')


def set_dart_subcommand(parents_parser):
    """
        parents_parser - subparsers
        """
    dart_cmd = ['save', 'analysis', 'analysis_1da']
    # create the parser for the "dart" command
    dart_parser = parents_parser.add_parser(
        'dart',
        description=f"Gather dart data and analysis",
        help='Gather dart data and analysis',
        epilog=f"Present addr - {present_addr}",
    )
    dart_parser.add_argument('dart_cmd', choices=dart_cmd)
    dart_parser.add_argument('-d', '--date', metavar='date', help='Set date(yyyymmdd)')
    dart_parser.add_argument('-m', '--message', action='store_true',
                             help='Send telegram message with result after work.')


def set_eval_subcommand(parents_parser):
    """
    parents_parser - subparsers
    """
    eval_cmd = ['report', 'spac']
    # create the parser for the "eval" command
    eval_parser = parents_parser.add_parser(
        'eval',
        description=f"Evaluating and reporting",
        help='Evaluating and reporting',
        epilog=f"Present addr - {present_addr}",
    )
    eval_parser.add_argument('eval_cmd', choices=eval_cmd)
    eval_parser.add_argument('-m', '--message', action='store_true', help='Send telegram message with result after work.')
    spiders_group = eval_parser.add_mutually_exclusive_group()
    spiders_group.add_argument('-c', '--code', metavar='code', help='Scrape one code')
    spiders_group.add_argument('-a', '--all', action='store_true', help='Scrape all codes')


def set_db_subcommand(parents_parser):
    """
    parents_parser - subparsers
    """
    db_cmd = ['set', 'print', 'sync']
    # create the parser for the "db" command
    db_parser = parents_parser.add_parser(
        'db',
        description=f"Help to set the mongo database address",
        help='Help to set the mongo database address',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    db_parser.add_argument('db_cmd', choices=db_cmd)
    db_parser.add_argument('-m', '--message', action='store_true', help='Send telegram message with result after work.')
    db_parser.add_argument('-a', '--addr', help='Set the address')


def scraper_if_flow(iargs):
    if iargs.scraper_cmd in spiders:
        if iargs.code:
            scraper_nfs.run(iargs.scraper_cmd, [iargs.code, ])
            if iargs.message:
                noti.telegram_to('manager',
                                 f'>>> python {os.path.basename(os.path.realpath(__file__))} scraper {iargs.scraper_cmd} -c {iargs.code}')
        elif iargs.all:
            scraper_nfs.run(iargs.scraper_cmd, list(krx.get_codes()))
            if iargs.message:
                noti.telegram_to('manager',
                                 f'>>> python {os.path.basename(os.path.realpath(__file__))} scraper {iargs.scraper_cmd} -a')
        sys.exit()
    elif iargs.scraper_cmd == 'mi':
        if iargs.message:
            noti.telegram_to('manager',
                             f'>>> python {os.path.basename(os.path.realpath(__file__))} scraper {iargs.scraper_cmd}')
        scraper_mi.mi()
        sys.exit()
    elif iargs.scraper_cmd == 'mi_hx':
        if iargs.message:
            noti.telegram_to('manager',
                             f'>>> python {os.path.basename(os.path.realpath(__file__))} scraper {iargs.scraper_cmd}')
        scraper_mi.mihistory(year=1)
        sys.exit()
    elif iargs.scraper_cmd == 'gm':
        pass
        sys.exit()


def refresh_if_flow(iargs):
    if iargs.refresh_cmd == 'run':
        # 해당 날짜의 끝자리에 해당하는 220여개의 krx 코드 파트와 refresh db에 저장된 코드의 합집합으로 하여 매일 실행한다.
        refreshing_codes = make_refresh_targets(client)
        if iargs.message:
            noti.telegram_to(botname='manager',
                             text=f'Starting.. c10346 scraper.. items : {len(refreshing_codes)}')
        scraper_nfs.run('c103', refreshing_codes)
        scraper_nfs.run('c104', refreshing_codes)
        scraper_nfs.run('c106', refreshing_codes)
        if iargs.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {iargs.refresh_cmd}')
        sys.exit()
    elif iargs.refresh_cmd == 'set_count':
        # dart중 해당날짜의 분기, 반기, 사업보고서를 검색하여 데이터베이스에 회사코드와 카운터, 날짜를 저장한다.
        # 하루에 한번만 실행한다. 반복실행하면 카운터가 계속 10으로 리셋된다.
        len_corp_refresh_table = opendart.Dart(client).set_refresh_count(datetime.datetime.today().strftime('%Y%m%d'))
        if iargs.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {iargs.refresh_cmd}\n'
                                  f'total items : {len_corp_refresh_table}')


def db_if_flow(iargs):
    if iargs.db_cmd == 'print':
        print(present_addr)
        sys.exit()
    elif iargs.db_cmd == 'sync':
        sync_mongo_with_krx(client)
        if iargs.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {iargs.db_cmd}')
        sys.exit()
    elif iargs.db_cmd == 'set':
        dbpath.save(f"mongodb://{iargs.addr}:27017")
        sys.exit()


def dart_if_flow(iargs):
    # -d 인자를 입력하면 해당날짜의 dart를 수집하고 생략하면 오늘날짜를 수집한다.
    if iargs.date:
        # 날짜입력이 형식에 맞는지 정규표현식으로 확인한다.
        p = re.compile('^20[0-9][0-9][0,1][0-9][0-3][0-9]$')
        if p.match(iargs.date) is None:
            print(f'Invalid date - {iargs.date}(YYYYMMDD)')
            sys.exit()
        else:
            date = iargs.date
    else:
        date = datetime.datetime.today().strftime('%Y%m%d')

    if iargs.dart_cmd == 'save':
        df = opendart.Dart(client).make_df(edate=date)
        mongo2.DartWithDate(client, date).save_df(df)
        if iargs.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {iargs.dart_cmd}\n'
                                  f'date : {date}\titems : {len(df)}')
        sys.exit()
    elif iargs.dart_cmd == 'analysis':
        print(f"Analysing {date} darts..")
        s_min, s_sec = divmod(analysis.run_all_subjects(date), 60)
        if iargs.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {iargs.dart_cmd}\n'
                                  f'spent time : {s_min}m {s_sec}s')
        sys.exit()
    elif iargs.dart_cmd == 'analysis_1da':
        date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        print(f"Analysing {date} darts..")
        s_min, s_sec = divmod(analysis.run_all_subjects(date), 60)
        if iargs.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {iargs.dart_cmd}\n'
                                  f'spent time : {s_min}m {s_sec}s')


def eval_if_flow(iargs):
    if iargs.eval_cmd == 'report':
        if iargs.code:
            print(report.for_console(client, iargs.code))
            if iargs.message:
                noti.telegram_to(botname='eval', text=report.for_telegram(client, iargs.code))
        elif iargs.all:
            df = eval.make_today_eval_df(present_addr)
            # pretty print df
            # https://www.delftstack.com/howto/python-pandas/how-to-pretty-print-an-entire-pandas-series-dataframe/
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', None)
            print(df)
            print("Save to mongo database...")
            mongo2.EvalWithDate(client, datetime.datetime.today().strftime('%Y%m%d'))

    elif iargs.eval_cmd == 'spac':
        for code, name, price in eval.yield_valid_spac(client):
            if iargs.message:
                noti.telegram_to(botname='eval',
                                 text=f'<<< code: {code} name: {name} price: {price} >>>')
        noti.telegram_to(botname='manager',
                         text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {iargs.subcommand}')


if __name__ == '__main__':
    # reference form https://docs.python.org/3.3/howto/argparse.html#id1
    parser = argparse.ArgumentParser(
        prog="nfs_manager",
        description="My Scraper program",
        epilog=f"Present addr - {present_addr}",
    )

    subparsers = parser.add_subparsers(
        title='Subcommands',
        description='valid subcommands',
        help='Additional help',
        dest="subcommand"
    )

    set_scraper_subcommand(subparsers)
    set_dart_subcommand(subparsers)
    set_refresh_subcommand(subparsers)
    set_eval_subcommand(subparsers)
    set_db_subcommand(subparsers)

    args = parser.parse_args()
    logger.debug(args)

    if args.subcommand == 'scraper':
        # cmd - c101, c108, c103, c104, c106, mi, mi_hx, gm
        scraper_if_flow(args)
    elif args.subcommand == 'dart':
        # cmd - save, analysis, analysis_1da
        dart_if_flow(args)
    elif args.subcommand == 'refresh':
        # cmd - run, set_count
        refresh_if_flow(args)
    elif args.subcommand == 'eval':
        # cmd - report, spac
        eval_if_flow(args)
    elif args.subcommand == 'db':
        # cmd - set, print, sync
        db_if_flow(args)
    else:
        parser.print_help()
        sys.exit()
