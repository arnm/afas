import click
import json
import cerberus
import nflgame.live
from InstagramAPI import InstagramAPI
import time

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


def constantly_annoy(instapi, followers):
    print followers

    def on_game_update(active, completed, diffs):

        for g in active:
            h, sh, a, sa = g.home, g.score_home, g.away, g.score_away
            print '%s :: %s (%d) vs. %s (%d)' % (g.time, h, sh, a, sa)

        # message opposing teams on events
        for diff in diffs:

            for play in diff.plays:
                print play.desc

            # direct message on scoring play
            scoring_team = ''
            if diff.before.score_away != diff.after.score_away:
                scoring_team = diff.before.away
            elif diff.before.score_home != diff.after.score_home:
                scoring_team = diff.before.home

            touchdown_plays = [play for play in diff.plays if play.touchdown]
            if touchdown_plays:
                # direct message on touchdown
                for touchdown_play in touchdown_plays:
                    people = [person['pk']
                              for person in followers if person['team'] == touchdown_play.team]
                    message = 'TOUCHDOWN %s!! %s!!' % (
                        touchdown_play.team, diff.plays[0].desc)

                    for person in people:
                        print '%s to %s' % (message, person)
                        instapi.direct_message(message, person)
                        time.sleep(2)
            elif scoring_team:
                # direct message on scoring play (not touchdown, field goal, safety, etc)
                people = [person['pk']
                          for person in followers if person['team'] != scoring_team]
                message = "I'LL TAKE THAT! LET'S GO %s! %s!" % (
                    scoring_team, diff.plays[0].desc)
                for person in people:
                    print '%s to %s' % (message, person)
                    instapi.direct_message(message, person)
                    time.sleep(2)

        for game in completed:
            # send group message to all losers
            losers = [loser['pk']
                      for loser in followers if loser['team'] == game.loser]

            winners = [winner['pk']
                       for winner in followers if winner['team'] == game.winner]

            loser_message = '%s WINNNSS!!! HAHAHA BETTER LUCK NEXT TIME!' % game.winner
            print 'messaging %s to %s' % (loser_message, losers)
            instapi.direct_message(loser_message, losers)

            winner_message = '%s WINNNSS!!! LETS GO!!' % game.winner
            print 'messaging %s to %s' % (winner_message, winners)
            instapi.direct_message(winner_message, winners)

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
    followers = {}
    for follower in config['followers']:
        followers[follower['username']] = {'team': follower['team']}

    for follower in instapi.getTotalFollowers(instapi.username_id):
        username = follower['username']
        if username in followers:
            followers[username].update(
                {'pk': follower['pk'], 'username': username})

    constantly_annoy(instapi, followers.values())


if __name__ == '__main__':
    cli()
