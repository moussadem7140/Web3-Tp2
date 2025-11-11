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
