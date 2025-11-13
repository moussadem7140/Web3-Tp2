"""Gestion du bluprint de compte utilisateur"""
import re
from flask import Blueprint, request, render_template, redirect, flash, session, url_for
import utils
import bd

bp_reservation = Blueprint('reservation', __name__)