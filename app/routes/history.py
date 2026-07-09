from flask import Blueprint, request, jsonify
from ..services.db_service import db_service

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
def get_history():
    limit = request.args.get('limit', 20, type=int)
    plant_filter = request.args.get('plant_type')
    user_id = request.args.get('user_id')
    
    try:
        results = db_service.get_detection_history(limit=limit, plant_filter=plant_filter, user_id=user_id)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
