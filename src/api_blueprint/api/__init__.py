"""
Flask-RESTful API Blueprint for MathPuzzle mobile clients and external integrations.
Provides REST endpoints for question fetching, answer validation, scoring, and leaderboard.
"""

from flask import Blueprint
from flask_restful import Api

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp, catch_all_404s=False)

# Import resources after creating api object to avoid circular imports
from .resources import (
    QuestionResource,
    AnswerResource,
    ScoreResource,
    LeaderboardResource,
    MultiplaryCreateResource,
    MultiplayerJoinResource,
    CategoriesResource,
    DifficultiesResource
)

# Register REST API endpoints
api.add_resource(CategoriesResource, '/categories')
api.add_resource(DifficultiesResource, '/difficulties')
api.add_resource(QuestionResource, '/question')
api.add_resource(AnswerResource, '/answer')
api.add_resource(ScoreResource, '/score')
api.add_resource(LeaderboardResource, '/leaderboard')
api.add_resource(MultiplaryCreateResource, '/multiplayer/create')
api.add_resource(MultiplayerJoinResource, '/multiplayer/join/<string:room_id>')
