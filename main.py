
from flask import Flask,render_template,request,flash
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from PIL import Image


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webp',  'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def resize_if_needed(img,max_width=1200):
    h,w=img.shape[:2]
    if w>max_width:
        ratio=max_width/w
        new_h=int(h*ratio)
        img = cv2.resize(img, (max_width, new_h), interpolation=cv2.INTER_AREA)
    return img

          
def processimage(filename,operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    base = filename.rsplit('.', 1)[0]
    match operation:
        case "cgray":
            imgprocessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            new_filename = f"{base}_gray.png"
            cv2.imwrite(f"static/{new_filename}", imgprocessed)
            return f"static/{new_filename}"
        case "cpng":
            new_filename = f"{base}.png"
            cv2.imwrite(f"static/{new_filename}", img)
            return f"static/{new_filename}"
        case "cwebp":
            new_filename = f"{base}.webp"
            cv2.imwrite(f"static/{new_filename}", img)
            return f"static/{new_filename}"
        case "cjpg":
            new_filename = f"{base}.jpg"
            cv2.imwrite(f"static/{new_filename}", img)
            return f"static/{new_filename}"
        case "csharp":
                kernel = np.array(
                    [[0, -1, 0],
                    [-1, 5, -1],
                    [0, -1, 0]])
                imgprocessed = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
                new_filename = f"{base}_sharp.png"
                cv2.imwrite(f"static/{new_filename}", imgprocessed)
                return f"static/{new_filename}"
        case "cmedian":
                imgprocessed = cv2.medianBlur(img,5)
                new_filename = f"{base}_smooth.png"
                cv2.imwrite(f"static/{new_filename}", imgprocessed)
                return f"static/{new_filename}"
        case "cpdf":
            image = Image.open(f"uploads/{filename}")
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            new_filename = f"{base}.pdf"
            image.save(f"static/{new_filename}", "PDF")
            return f"static/{new_filename}"
        case "ccompress":
            img = resize_if_needed(img)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{base}_compressed.{ext}"
            if ext in ("jpg","jpeg"):
                cv2.imwrite(
                    f"static/{new_filename}",
                    img,
                    [cv2.IMWRITE_JPEG_QUALITY, 60]
                )
            elif ext=="png":
                cv2.imwrite(
                    f"static/{new_filename}",
                    img,
                    [cv2.IMWRITE_PNG_COMPRESSION, 9]
                )
            elif ext=="webp":
                cv2.imwrite(
                    f"static/{new_filename}",
                    img,
                    [cv2.IMWRITE_WEBP_QUALITY, 60]
                )
            else:
                return None
            return f"static/{new_filename}"
        
    



@app.route('/')

def home():
    return render_template("index.html")
@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/edit',methods=["GET","POST"])
def edit():
    if request.method == 'POST':
        operation=request.form.get("operation")
        if 'file' not in request.files:
               flash('No file part')
               return "error"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "error: no file selected"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new=processimage(filename,operation)
            if new is None:
                flash("Compression failed or operation not supported")
                return render_template("index.html")

            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            return render_template("index.html")
    return render_template("index.html")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


