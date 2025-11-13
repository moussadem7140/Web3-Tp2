"""
Connexion à la BD
"""
import types
import contextlib
import mysql.connector

@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user='garneau',
        password='qwerty_123',
        host='127.0.0.1',
        database='services_particuliers',
        raise_on_warnings=True
    )

    # Pour ajouter la méthode getCurseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir les enregistrements sous forme de dictionnaires"""
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()

def get_services(conn, tous = False):
    with conn.get_curseur() as curseur:
        if tous:
            curseur.execute('''SELECT s.id_service, s.titre, s.localisation, s.date_creation,s.photo, c.nom_categorie
                            FROM services s JOIN categories c ON s.id_categorie = c.id_categorie
                                 ORDER By s.date_creation''')
            return curseur.fetchall()
        else:
            curseur.execute('''SELECT s.id_service, s.titre, s.localisation, s.date_creation, s.photo, c.nom_categorie
                    FROM services s JOIN categories c ON s.id_categorie = c.id_categorie
                    WHERE s.actif = 1 ORDER BY s.date_creation limit 5''')
            return curseur.fetchall()

def get_service(conn, id_service):
       with conn.get_curseur() as curseur:
                curseur.execute('''SELECT s.id_service, s.titre, s.localisation, s.description, s.cout, s.date_creation, s.actif, c.nom_categorie
                            FROM services s JOIN categories c ON s.id_categorie = c.id_categorie
                            WHERE s.id_service = %(id)s''',
                {
                    "id": id_service
                })
                return curseur.fetchone()

def add_service(conn, service):
        with conn.get_curseur() as curseur:
                curseur.execute('''INSERT INTO services(titre, description,localisation, actif, cout, id_categorie, date_creation, photo)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', (service['titre'],service['description'], service['localisation'], service['actif'], service['cout'], service['id_categorie'], service['date_creation'], service['photo']))

def get_categories(conn):
      with conn.get_curseur() as curseur:
            curseur.execute("""
            SELECT id_categorie, nom_categorie FROM categories """)
            return curseur.fetchall()
def update_service(conn, id_service, titre, localisation, description, cout, actif):
        with conn.get_curseur() as curseur:
                curseur.execute('''UPDATE services
                            SET titre = %s, localisation = %s, description = %s, cout =%s, actif = %s
                            WHERE id_service = %s''', (titre, localisation, description, cout, actif, id_service))

def creer_user(conn,user):
    """ Permet d'ajouter un utilisateur dans la bd"""
    with conn.get_curseur() as curseur:
        curseur.execute("""INSERT INTO `utilisateur` (`courriel`, `mdp`, `role`, `credit`)
                           VALUES (%(courriel)s, %(mdp)s, %(role)s, %(credit)s)""",user)


def authentification(conn,courriel,mdp):
    """ Permet de verifier l'identifiant de l'utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute("""SELECT *
                        FROM utilisateur WHERE courriel= %(courriel)s AND mdp=%(mdp)s""",
                        {
                            "courriel": courriel,
                            "mdp": mdp
                        })
        user = curseur.fetchone()
        return user

def verifie_doublon_courriel(conn, courriel):
    "Retourne true si le courriel est utilisé false si non"
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT courriel FROM utilisateur WHERE courriel= %(courriel)s",
                         {"courriel": courriel})
        user = curseur.fetchone()

        return user

def get_liste_compte(conn):
    """Tous les services"""
    with conn.get_curseur() as curseur:
            curseur.execute('''SELECT id_utilisateur, courriel, role, credit FROM utilisateur''')
            user =curseur.fetchall()
            return user

def ajouter_utilisateur(conn, nom, courriel, hashed, credit, role):
    """Ajoute un utilisateur dans la base de données"""
    with conn.get_curseur() as curseur:
        if role == 'admin':
            curseur.execute(
                """
                INSERT INTO utilisateur (nom, courriel, mdp, role, credit)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nom, courriel, hashed, 'user', credit)
            )
            conn.commit()

def get_supprimer_utilisateur(conn, id_utilisateur):
    """Supprime un utilisateur de la base de données (admin seulement)."""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "DELETE FROM utilisateur WHERE id_utilisateur = %s",
            (id_utilisateur,)
        )
        conn.commit()
