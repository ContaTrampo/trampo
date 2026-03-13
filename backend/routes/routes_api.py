"""TRAMPO v7 — Rota de rotas (trajetos)"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

routes_bp = Blueprint("routes_calc", __name__, url_prefix="/api/routes")


@routes_bp.route("/estimate", methods=["POST"])
@jwt_required()
def estimate_route():
    data = request.get_json() or {}
    return jsonify({"message": "Rota estimada (em breve com Google Maps)", "data": data}), 200
