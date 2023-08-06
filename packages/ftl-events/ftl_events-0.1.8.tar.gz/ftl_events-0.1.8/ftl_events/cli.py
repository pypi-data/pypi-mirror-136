

"""
Usage:
    ftl-events [options] <rules.yml>

Options:
    -h, --help            Show this page
    -v, --vars=<v>        Variables file
    -i, --inventory=<i>   Inventory
    --env-vars=<e>        Comma separated list of variables to import from the environment
    --redis_host_name=<h> Redis host name
    --redis_port=<p>      Redis port
    --debug               Show debug logging
    --verbose             Show verbose logging
"""
from docopt import docopt
import os
import logging
import sys
import yaml
import ftl_events.rules_parser as rules_parser
import ftl_events.rule_generator as rule_generator
from ftl_events.durability import provide_durability
import multiprocessing as mp
import runpy
import jinja2
import asyncio
import durable.lang
from urllib.parse import urlparse
from faster_than_light import run_module, load_inventory

logger = logging.getLogger('cli')


def load_vars(parsed_args):
    variables = dict()
    if parsed_args['--vars']:
        with open(parsed_args['--vars']) as f:
            variables.update(yaml.safe_load(f.read()))

    if parsed_args['--env-vars']:
        for env_var in parsed_args['--env-vars'].split(','):
            env_var = env_var.strip()
            if env_var not in os.environ:
                raise KeyError(f'Could not find environment variable "{env_var}"')
            variables[env_var] = os.environ[env_var]

    return variables

def load_rules(parsed_args):
    with open(parsed_args['<rules.yml>']) as f:
        return rules_parser.parse_rule_sets(yaml.safe_load(f.read()))


def substitute_variables(value, context):
    return jinja2.Template(value, undefined=jinja2.StrictUndefined).render(context)


def start_sources(sources, variables, queue):

    logger = mp.get_logger()
    #logger.setLevel(logging.INFO)

    logger.info('start_sources')

    for source in sources:
        module = runpy.run_path(os.path.join('sources', source.source_name + '.py'))
        args = {k: substitute_variables(v, variables) for k, v in source.source_args.items()}
        module.get('main')(queue, args)


def run_ruleset(ruleset, variables, inventory, queue, redis_host_name=None, redis_port=None):

    logger = mp.get_logger()
    #logger.setLevel(logging.INFO)

    logger.info('run_ruleset')

    if redis_host_name and redis_port:
        provide_durability(durable.lang.get_host(), redis_host_name, redis_port)

    logger.info(str([ruleset]))
    durable_ruleset = rule_generator.generate_rulesets([ruleset], variables)
    logger.info(str([x.define() for x in durable_ruleset]))

    while True:
        logger.info("Waiting for event")
        data = queue.get()
        logger.info(str(data))
        if not data:
            continue
        logger.info(str(data))
        logger.info(str(ruleset.name))
        try:
            logger.info('Asserting event')
            durable.lang.assert_fact(ruleset.name, data)
            logger.info('Retracting event')
            durable.lang.retract_fact(ruleset.name, data)
        except durable.engine.MessageNotHandledException:
            logger.error(f'MessageNotHandledException: {data}')

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = docopt(__doc__, args)
    if parsed_args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    logger = mp.log_to_stderr()
    logger.setLevel(logging.INFO)
    variables = load_vars(parsed_args)
    rulesets = load_rules(parsed_args)
    inventory = load_inventory(parsed_args['--inventory'])

    logger.info(f"Variables: {variables}")
    logger.info(f"Rulesets: {rulesets}")

    tasks = []

    for ruleset in rulesets:
        sources = ruleset.sources
        queue = mp.Queue()

        tasks.append(mp.Process(target=start_sources, args=(sources, variables, queue)))
        tasks.append(mp.Process(target=run_ruleset, args=(ruleset, variables, inventory, queue, parsed_args['--redis_host_name'], parsed_args['--redis_port'])))

    logger.info('Starting processes')
    for task in tasks:
        task.start()

    logger.info('Joining processes')
    for task in tasks:
        task.join()

    return 0

def entry_point():
    main(sys.argv[1:])
