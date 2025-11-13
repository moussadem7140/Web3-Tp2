"""Gestion du bluprint de compte utilisateur"""
import re
from flask import Blueprint, request, render_template, redirect, flash, session, url_for, abort
import utils
import bd

bp_reservation = Blueprint('reservation', __name__)

@bp_reservation.route('/reservation', methods=['GET'])
def reservation():
    """deconnecter"""
    return render_template("reservation/reservation.jinja")

