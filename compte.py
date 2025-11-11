"""Gestion du bluprint de compte utilisateur"""
import re
from flask import Blueprint, request, render_template, redirect, flash, session, url_for
import utils
import bd

bp_compte = Blueprint('compte', __name__)

#regex pour verifier s'il y a une balise html dans les champs
REGEXE_EMAIL = re.compile(r"^(?!.*\.\.)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")
REGEX_MDP = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$")
REGEX_HTML = re.compile(r"<[^>]+>")

