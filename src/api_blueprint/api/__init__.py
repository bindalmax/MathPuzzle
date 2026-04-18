"""
Flask-RESTful API Blueprint for MathPuzzle mobile clients and external integrations.
Provides REST endpoints for question fetching, answer validation, scoring, and leaderboard.
"""

from flask import Blueprint
from flask_restful import Api
from .resources import (
    QuestionResource,
    AnswerResource,
    ScoreResource,
    LeaderboardResource,
    MultiplaryCreateResource,
    MultiplayerJoinResource,
    MultiplayerRoomsResource,
    MultiplayerResultsResource,
    GoogleAuthResource,
    CategoriesResource,
    DifficultiesResource
)

# Initialize Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# Register REST API endpoints
api.add_resource(CategoriesResource, '/categories')
api.add_resource(DifficultiesResource, '/difficulties')
api.add_resource(QuestionResource, '/question')
api.add_resource(AnswerResource, '/answer')
api.add_resource(ScoreResource, '/score')
api.add_resource(LeaderboardResource, '/leaderboard')
api.add_resource(MultiplaryCreateResource, '/multiplayer/create')
api.add_resource(MultiplayerJoinResource, '/multiplayer/join/<string:room_id>')
api.add_resource(MultiplayerRoomsResource, '/multiplayer/rooms')
api.add_resource(MultiplayerResultsResource, '/multiplayer/results/<string:room_id>')
api.add_resource(GoogleAuthResource, '/auth/google')
