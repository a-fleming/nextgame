import math
import sqlite3

from datetime import date

from nextgame.commands.common import open_db
from nextgame.db.queries.game_tags import get_tags_by_game_id
from nextgame.db.queries.games import get_all_games
from nextgame.db.queries.sessions import get_total_sessions_and_recent_play_by_game
from nextgame.db.queries.tags import get_tag_ids_by_names
from nextgame.validation import error_if_tag_options_conflict, error_if_weight_options_conflict

CATEGORY_PERCENTAGES = {  # relative weight percentages of the possible score categories when computing composite score
    "exclude_tags": 20,
    "include_tags": 20,
    "last_played_on": 10,
    "time": 25,
    "total_sessions": 5,
    "weight": 20,
}
DEFAULT_LIMIT = 5  # default maximum number of recommended results to show
EXP_DECAY_RATE = 0.05 # regain 50% time score about 14 days after last play
MAX_CATEGORY_POINTS = 100  # maximum points available within each scoring category
MAX_WEIGHT = 5.0  # maximum possible game weight
MIN_WEIGHT = 1.0  # minimum possible game weight
WEIGHT_VALUE_RANGE = MAX_WEIGHT - MIN_WEIGHT


def cmd_recommend(args):
    error_if_tag_options_conflict(args)
    error_if_weight_options_conflict(args)

    with open_db(args.db_path) as conn:
        # Determine scoring categories
        score_categories = ["last_played_on", "total_sessions"]  # always used for scoring
        if args.time:
            score_categories.append("time")
        if args.max_weight or args.min_weight:
            score_categories.append("weight")

        if args.include_tags:
            score_categories.append("include_tags")
            incl_tags = list(dict.fromkeys(args.include_tags))  # remove duplicates
            incl_tag_names_to_ids = get_tag_ids_by_names(conn, incl_tags)
            unknown = [tag_name for tag_name in incl_tags if tag_name not in incl_tag_names_to_ids]
            if unknown:
                args.parser.error(
                f"Unknown include tag{'' if len(unknown) == 1 else 's'} specified: {', '.join(unknown)}."
            )

        if args.exclude_tags:
            score_categories.append("exclude_tags")
            excl_tags = list(dict.fromkeys(args.exclude_tags))  # remove duplicates
            excl_tag_names_to_ids = get_tag_ids_by_names(conn, excl_tags)
            unknown = [tag_name for tag_name in excl_tags if tag_name not in excl_tag_names_to_ids]
            if unknown:
                args.parser.error(
                f"Unknown exclude tag{'' if len(unknown) == 1 else 's'} specified: {', '.join(unknown)}."
            )

        all_games: list[sqlite3.Row] = get_all_games(conn)
        game_tags_by_name: dict[str, dict[str, int]] = {}  # mapping from game name to dict of tag names to IDs
        game_sessions_by_name: dict[str, dict] = get_total_sessions_and_recent_play_by_game(conn)  # mapping from game names to dict of session counts and recent plays
        valid_games = filter_games_by_players(all_games, args.players)
        valid_game_names = [g['name'] for g in valid_games]
        total_valid_game_sessions = sum([vals["total_sessions"] for name, vals in game_sessions_by_name.items() if name in valid_game_names])
        if not valid_games:
            print(f"No games found for {args.players} players")
            return
        
        game_scores: dict[str, dict[str, float]] = {}  # mapping from game names to dictionary of score categories to score
        for game in valid_games:
            score = {}
            game_id = game["game_id"]
            game_name = game["name"]
            game_time = game["est_avg_minutes"]
            game_weight = game["weight"]
            tags: dict[str, int] = get_tags_by_game_id(conn, game_id)
            game_tags_by_name[game_name] = tags
            
            score["total_sessions"] = compute_total_sessions_score(game_name, game_sessions_by_name, total_valid_game_sessions)
            score["last_played_on"] = compute_last_played_on_score(game_name, game_sessions_by_name)

            if args.time:
                score["time"] = compute_time_score(game_time, args.time)
                
            if args.min_weight or args.max_weight:
                score["weight"] = compute_weight_score(game_weight, args.min_weight, args.max_weight)
                
            if args.include_tags or args.exclude_tags:
                game_tag_set = set(game_tags_by_name.get(game_name, []))
                
                if args.include_tags:
                    score["include_tags"] = compute_include_tags_score(game_tag_set, args.include_tags)
                    
                if args.exclude_tags:
                    score["exclude_tags"] = compute_exclude_tags_score(game_tag_set, args.exclude_tags)
                    
            score["composite"] = compute_composite_score(score, score_categories)
            game_scores[game_name] = score

    result_limit = args.limit or DEFAULT_LIMIT
    sorted_scores = sort_games_by_composite_scores(game_scores)
    for idx, game_name in enumerate(list(sorted_scores)[:result_limit], start=1):
        print(f"{idx}. '{game_name}' ({game_scores[game_name]["composite"]:0.2f}% match)")

def compute_composite_score(game_score: dict[str, float], score_categories: list[str]) -> float:
    total_score = 0
    total_percents = 0
    for category in score_categories:
        category_percent = CATEGORY_PERCENTAGES[category]
        total_percents += category_percent
        total_score += category_percent * game_score[category]
    return total_score / total_percents

def compute_exclude_tags_score(game_tag_set: set[str], unwanted_tags: list[str]) -> float:
    # Remove points for each unwanted tag that is included
    excl_tag_set = set(unwanted_tags)
    unwanted_but_have = excl_tag_set & game_tag_set

    points_per_tag = MAX_CATEGORY_POINTS / len(excl_tag_set)
    point_deduction = points_per_tag * len(unwanted_but_have)
    return max(MAX_CATEGORY_POINTS - point_deduction, 0)  # prevent negative score

def compute_include_tags_score(game_tag_set: set[str], wanted_tags: list[str]) -> float:
    # Remove points for each wanted tag that is missing
    incl_tag_set = set(wanted_tags)
    wanted_but_missing = incl_tag_set - game_tag_set
    points_per_tag = MAX_CATEGORY_POINTS / len(incl_tag_set)
    point_deduction = points_per_tag * len(wanted_but_missing)
    return max(MAX_CATEGORY_POINTS - point_deduction, 0)  # prevent negative score

def compute_last_played_on_score(game_name: str, game_sessions_by_name: dict[str, dict]) -> float:
    if game_name not in game_sessions_by_name:
        return MAX_CATEGORY_POINTS
    else:
        last_played_on = game_sessions_by_name[game_name]["last_played_on"]
        date_played = date.fromisoformat(last_played_on)
        today = date.today()
        days_since_played = (today - date_played).days
        
        # use exponential decay to penalize recently played games
        recency_penalty_pct = math.exp(-days_since_played * EXP_DECAY_RATE)
        point_deduction = MAX_CATEGORY_POINTS * recency_penalty_pct
        return max(MAX_CATEGORY_POINTS - point_deduction, 0)  # prevent negative score

def compute_time_score(game_time: int, time_range: tuple) -> float:
    time_lower_limit, time_upper_limit = time_range
    if time_lower_limit <= game_time <= time_upper_limit:
        time_difference = 0
    elif game_time < time_lower_limit:
        time_difference = time_lower_limit - game_time
    else: # time_upper_limit < game_time
        time_difference = game_time - time_upper_limit
        
    time_value_range = max(time_upper_limit - 1, 1)  # prevent division by 0
    points_per_increment = MAX_CATEGORY_POINTS / time_value_range
    point_deduction = points_per_increment * time_difference
    return max(MAX_CATEGORY_POINTS - point_deduction, 0)  # prevent negative score

def compute_total_sessions_score(game_name: str, game_sessions_by_name: dict[str, dict], total_valid_game_sessions: int) -> float:
    if game_name not in game_sessions_by_name:
        return MAX_CATEGORY_POINTS
    total_sessions = game_sessions_by_name[game_name]["total_sessions"]
    point_deduction = (total_sessions * 100) // total_valid_game_sessions # penalize games proportionately to how often they have been played
    return max(MAX_CATEGORY_POINTS - point_deduction, 0)  # prevent negative score

def compute_weight_score(game_weight: float, desired_min_weight: float, desired_max_weight: float) -> float:
    if game_weight is None:
        # Score for unknown weight is based on how much of the possible weight range is taken up by the desired range
        if desired_min_weight and desired_max_weight:
            pct_coverage = (desired_max_weight - desired_min_weight) / WEIGHT_VALUE_RANGE
        elif desired_min_weight:
            pct_coverage = (desired_min_weight - MIN_WEIGHT) / WEIGHT_VALUE_RANGE
        else:  # only desired_max_weight
            pct_coverage = (MAX_WEIGHT - desired_max_weight) / WEIGHT_VALUE_RANGE
        return pct_coverage * MAX_CATEGORY_POINTS

    # Game weight is known
    if desired_min_weight and desired_max_weight:
        if desired_min_weight <= game_weight <= desired_max_weight:
            return MAX_CATEGORY_POINTS
        
    # If weight is not within specified min/max it can only be either below the min or above the max
    # Similarly, if only one of min/max was specified, we only care about weight in relation to that one criteria
    weight_difference = 0
    if desired_min_weight and game_weight < desired_min_weight:
        weight_difference = desired_min_weight - game_weight
    elif desired_max_weight and desired_max_weight < game_weight:
        weight_difference = game_weight - desired_max_weight
    else:
        # If not below min or above max, we are within specified range
        return MAX_CATEGORY_POINTS
    
    # Remove points based on how much the game weight is outside the desired weight range
    points_per_increment = MAX_CATEGORY_POINTS / WEIGHT_VALUE_RANGE
    point_deduction = points_per_increment * weight_difference
    return max(MAX_CATEGORY_POINTS - point_deduction, 0)

def filter_games_by_players(games: list[sqlite3.Row], players: int) -> list[sqlite3.Row]:
    filtered = []
    for game in games:
        min_players = game["min_players"]
        max_players = game["max_players"]
        if min_players <= players <= max_players:
            filtered.append(game)
    return filtered

def sort_games_by_composite_scores(all_game_scores: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    def by_composite_score(name_and_scores: tuple[str, dict[str, float]]) -> float:
        _name, scores = name_and_scores
        return scores["composite"]
    return dict(sorted(all_game_scores.items(), key=by_composite_score, reverse=True))
