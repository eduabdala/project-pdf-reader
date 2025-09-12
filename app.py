from flask import Flask, render_template, request, send_from_directory, jsonify
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# ==============================
# Configurações do Flask e DB
# ==============================

app = Flask(__name__)

# Banco de dados SQLite
DB_PATH = "progress.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Model para guardar progresso
class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    file_name = Column(String, unique=True, nullable=False)
    last_page = Column(Integer, default=0, nullable=False)

Base.metadata.create_all(engine)


# ==============================
# Rotas
# ==============================

@app.route("/")
def index():
    """
    Página inicial: mostra lista de PDFs disponíveis no diretório `static/pdfs/`
    (poderia ser melhorada para upload, mas simplificamos aqui).
    """
    pdf_folder = os.path.join(app.static_folder, "pdfs")
    pdf_files = []
    if os.path.exists(pdf_folder):
        for fname in os.listdir(pdf_folder):
            if fname.lower().endswith(".pdf"):
                pdf_files.append(fname)
    return render_template("index.html", pdf_files=pdf_files)

@app.route("/reader/<pdf_name>")
def reader(pdf_name):
    """
    Mostrar página de leitura de um PDF específico.
    Usa template que carrega PDF.js para visualização.
    Também consulta o DB para ver qual página foi lida por último.
    """
    # Verifica se o arquivo existe
    pdf_path = os.path.join(app.static_folder, "pdfs", pdf_name)
    if not os.path.exists(pdf_path):
        return "PDF não encontrado", 404

    # Busca progresso no DB
    session = Session()
    prog = session.query(Progress).filter_by(file_name=pdf_name).first()
    last_page = prog.last_page if prog else 1
    session.close()

    return render_template("reader.html", pdf_name=pdf_name, last_page=last_page)

@app.route("/save_progress", methods=["POST"])
def save_progress():
    """
    Recebe requisição AJAX do front-end informando o PDF e a página atual, e salva no DB.
    """
    data = request.json
    pdf_name = data.get("pdf_name")
    page = data.get("page")

    if pdf_name is None or page is None:
        return jsonify({"status": "error", "message": "Dados incompletos"}), 400

    session = Session()
    prog = session.query(Progress).filter_by(file_name=pdf_name).first()
    if prog:
        prog.last_page = page
    else:
        prog = Progress(file_name=pdf_name, last_page=page)
        session.add(prog)
    session.commit()
    session.close()

    return jsonify({"status": "ok"})

@app.route('/static/pdfs/<path:filename>')
def serve_pdf(filename):
    """
    Serve arquivos PDF estáticos.
    """
    return send_from_directory(os.path.join(app.static_folder, "pdfs"), filename)

if __name__ == "__main__":
    app.run(debug=True)
