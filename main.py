from flask import Flask, render_template, request, flash, url_for
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, validators, FileField
from flask_uploads import UploadSet, configure_uploads, IMAGES


Base = declarative_base()
app = Flask(__name__)
app.secret_key = 'secret'


# Database setting

# Business Information
class BusinessInfo(Base):
    __tablename__ = "business"

    id = Column('id', Integer, primary_key=True)
    company = Column('company', String)
    companydesc = Column('companydesc', String)
    locationname = Column('locationname', String)
    address = Column('address', String)
    hotline = Column('hotline', Integer)
    email = Column('email', String)
    website = Column('website', String)
    operatinghours = Column('operatinghours', String)
    filename = Column('filename', String)
    # Relationship
    feed = relationship('Feed')

    def __init__(self, company, companydesc, locationname, address, hotline, email, website, operatinghours, filename):
        self.company = company
        self.companydesc = companydesc
        self.locationname = locationname
        self.address = address
        self.hotline = hotline
        self.email = email
        self.website = website
        self.operatinghours = operatinghours
        self.filename = filename

    def get_company(self):
        return self.company

    def get_desc(self):
        return self.companydesc

    def get_location(self):
        return self.locationname

    def get_address(self):
        return self.address

    def get_hotline(self):
        return self.hotline

    def get_email(self):
        return self.email

    def get_website(self):
        return self.website

    def get_operating(self):
        return self.operatinghours

    def get_filename(self):
        return self.filename


# Business Page Gallery & Blogs
class Feed(Base):
    __tablename__ = 'feed'
    id = Column('id', Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('business.id'))
    business_info = relationship('BusinessInfo')
    blogger = Column('blogger', String)
    blog = Column('blog', String)
    filename = Column('filename', String)

    def __init__(self, blogger, blog, filename):
        self.blogger = blogger
        self.blog = blog
        self.filename = filename

    def get_blogger(self):
        return self.blogger

    def get_blog(self):
        return self.blog

    def get_filename(self):
        return self.filename


# Retrieve and insert Image File
engine = create_engine('sqlite:///business.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
list = []


def matchdb_retrieve():
    global list
    list.clear()
    session = Session()
    business = session.query(BusinessInfo).all()
    for businesses in business:
        list.append(businesses)
    session.close()
    return len(list)


photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/avatars'
configure_uploads(app, photos)


#
engine = create_engine('sqlite:///feed.db', echo=True)
Base.metadata.create_all(bind=engine)
Session1 = sessionmaker(bind=engine)
list = []


def profiledb_retrieve():
    global list
    list.clear()
    session = Session()
    feed = session.query(Feed).all()
    for feeds in feed:
        list.append(feeds)
    session.close()
    return len(list)


photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/galleries'
configure_uploads(app, photos)


# Flask WTForms
class RegisterForm(FlaskForm):
    company = StringField('Business Name :', [
        validators.Length(min=1, max=50),
        validators.Required()
    ])
    companydesc = TextAreaField('Business Description :', [validators.Length(min=1, max=500), validators.Required()])
    locationname = StringField('Location Name :', [validators.Length(min=3, max=100), validators.Required()])
    address = StringField('Address :', [validators.Length(min=3, max=100), validators.Required()])
    hotline = StringField('Hotline :', [validators.Length(min=8, max=50), validators.Required()])
    email = StringField('Business E-mail :', [validators.Length(min=6, max=50), validators.Required()])
    website = StringField('Website URL(Optional) :')
    operatinghours = TextAreaField('Operating Hours :', [validators.Required()])
    submit = SubmitField("Create Business")


class PostUpdate(FlaskForm):
    blogger = "get_current_user"
    blog = TextAreaField("Status update", [validators.Length(min=1, max=1500), validators.Required()])
    submit1 = SubmitField("Post")


@app.route("/")
def main():
    return "Hello World!"


@app.route('/register', methods=['GET', 'POST'])
def form():
    form = RegisterForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit() and "photo" in request.files:
            name = form.company.data
            desc = form.companydesc.data
            location = form.locationname.data
            address = form.address.data
            hotline = form.hotline.data
            email = form.email.data
            website = form.website.data
            operatinghours = form.operatinghours.data
            filename = photos.save(request.files["photo"])
            session = Session()

            session.add(BusinessInfo(name, desc, location, address, hotline, email, website, operatinghours, filename))
            session.commit()
            session.close()
            flash('success')
            return render_template('addBusiness.html', form=form)
        else:
            flash('All fields are required.')
            return "u"
    elif request.method == 'GET':
        return render_template('addBusiness.html', form=form)


@app.route("/<name>", methods=['GET', 'POST'])
def status(name):
    form = PostUpdate(request.form)

    if request.method == 'POST':
        if form.validate_on_submit() and "photo" in request.files:
            blogger = "ded"
            blog = form.blog.data
            filename = photos.save(request.files["photo"])
            session = Session()

            session.add(Feed(blogger, blog, filename))
            session.commit()
            session.close()
            flash('success')
            return render_template('businessProf.html', form=form, name=name)
        else:
            flash('All fields are required.')
            return "u"
    elif request.method == 'GET':
        return render_template('businessProf.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)