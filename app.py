from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://qianyang:@localhost/pokemon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True
db = SQLAlchemy(app)

@app.before_first_request
def create_db():
    # Recreate database each time for demo
    db.create_all()


class Pokemon(db.Model):
    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(100))
    attack = db.Column(db.Integer)

class PokemonForm(FlaskForm):
    id = IntegerField("Pokemon ID: ")
    name = StringField("Pokemon Name: ", validators=[DataRequired()])
    type = StringField("Pokemon Type: ", validators=[DataRequired()])
    attack = IntegerField("Pokemon Attack: ", validators=[DataRequired()])



@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form.get('pokemon_name')
        results = Pokemon.query.filter(Pokemon.name.like('%{}%'.format(name))).all()
        return render_template('master.html', pokemons=results, pageTitle="Pokemons", legend="Search Results")
    else:
        return redirect('/')

@app.route("/")
def index():
    pokemons = list(Pokemon.query.order_by(Pokemon.id))
    return render_template("master.html", pokemons=pokemons, pageTitle="Pokemons")


@app.route("/detail/<int:id>", methods=['GET','POST'])
def detail(id):
    pokemon = Pokemon.query.filter_by(id=id).one()

    form = PokemonForm()

    form.id.data = pokemon.id
    form.name.data = pokemon.name
    form.type.data = pokemon.type
    form.attack.data = pokemon.attack

    return render_template('detail.html',form=form, pageTitle='Pokemon Details', legend="Pokemon Details")


@app.route("/add", methods=['GET', 'POST'])
def add_pokemon():
    form = PokemonForm()
    if form.validate_on_submit():
        db.session.add(Pokemon(name=form.name.data, type=form.type.data, attack=form.attack.data))
        db.session.commit()
        return redirect('/')
    
    return render_template('add_pokemon.html', form=form, pageTitle='Add A New Pokemon',
                            legend="Add A New Pokemon")


@app.route("/update/<int:id>", methods=["POST"])
def update_pokemon(id):
    pokemon = Pokemon.query.get_or_404(id)
    form = PokemonForm()
    if form.validate_on_submit():
        pokemon.name = form.name.data
        pokemon.type = form.type.data
        pokemon.attack = form.attack.data
        db.session.commit()
        flash("Pokemon updated", "success") 
        return redirect(url_for('detail', id=pokemon.id))

    form.id.data = pokemon.id
    form.name.data = pokemon.name
    form.type.data = pokemon.type
    form.attack.data = pokemon.attack
    return render_template('update_pokemon.html', form=form, pageTitle='Update Pokemon', legend="Update A Pokemon")

@app.route("/delete/<int:id>", methods=("POST","GET"))
def delete_pokemon(id):
    if request.method == 'POST':
        pokemon = Pokemon.query.get_or_404(id)
        db.session.delete(pokemon)
        db.session.commit()
        flash("Pokemon deleted", "warning")
        return redirect('/')
    return redirect('/')


if __name__ == "__main__":
    app.run()
