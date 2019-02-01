import click
import json
import cerberus
import nflgame.live
from InstagramAPI import InstagramAPI

CONFIG_SCHEMA = {
    'username': {'type': 'string', "empty": False, "required": True},
    'password': {'type': 'string', "empty": False, "required": True},
    'followers': {
        "empty": False,
        "required": True,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'username': {'type': 'string', 'required': True, 'empty': False},
                'team': {'type': 'string', 'required': True, 'empty': False}
            }
        }
    }
}


def get_config(path, schema):
    validator = cerberus.Validator(schema)

    with open(path) as f:
        config = json.load(f)

        if not validator.validate(config):
            raise click.ClickException(
                'invalid config: ' + str(validator.errors))

        return config


def constantly_annoy(instapi, to_annoy):
    print to_annoy

    def on_game_update(active, completed, diffs):

        for g in active:
            h, sh, a, sa = g.home, g.score_home, g.away, g.score_away
            print '%s :: %s (%d) vs. %s (%d)' % (g.time, h, sh, a, sa)

        # message opposing teams on events
        for diff in diffs:

            if [play for play in diff.plays if play.touchdown]:
                print 'touchdown'
                continue

            if diff.before.score_away != diff.after.score_away:
                print 'home scored'

            if diff.before.score_home != diff.after.score_home:
                print 'home scored'

        for game in completed:
            # messsage all losers
            losers = [loser['pk']
                      for loser in to_annoy if loser['team'] == game.loser]

            instapi.direct_message('%s WINNNSS!!! HAHAHA BETTER LUCK NEXT TIME!' %
                                   game.winner, losers)

    nflgame.live.run(on_game_update)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--path', default='config.json', help='config file path')
def annoy(path):
    config = get_config(path, CONFIG_SCHEMA)

    instapi = InstagramAPI(config['username'], config['password'])
    instapi.login()

    # build easier to work with dict
    # by joining on key username
    # e.g { 'instausername': { 'username': 'instausername', pk': 12345, 'team': 'Pat' } }
    to_annoy = {}
    for follower in config['followers']:
        to_annoy[follower['username']] = {'team': follower['team']}

    for follower in instapi.getTotalFollowers(instapi.username_id):
        username = follower['username']
        if username in to_annoy:
            to_annoy[username].update(
                {'pk': follower['pk'], 'username': username})

    constantly_annoy(instapi, to_annoy.values())


if __name__ == '__main__':
    cli()
