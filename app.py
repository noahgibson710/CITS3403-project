<<<<<<< HEAD
from app import create_app

app = create_app()
=======
from app import app

>>>>>>> c4ad442 (changed directories to support server side jinja rendering)

if __name__ == '__main__':
    app.run(debug=True)
