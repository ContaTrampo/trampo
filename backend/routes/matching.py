"""TRAMPO v7 — Matching API"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.matching_engine import find_top_jobs, find_top_candidates

matching_bp = Blueprint("matching", __name__, url_prefix="/api/matching")


@matching_bp.route("/my-jobs", methods=["GET"])
@jwt_required()
def my_matches():
    user_id   = int(get_jwt_identity())
    min_score = float(request.args.get("min_score", 0))
    limit     = int(request.args.get("limit", 20))
    jobs = find_top_jobs(user_id, limit=limit, min_score=min_score)
    return jsonify({"jobs": jobs, "total": len(jobs)}), 200
