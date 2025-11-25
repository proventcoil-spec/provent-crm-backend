
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from extensions import db
from models import Event, MediaFile

uploads_bp = Blueprint("uploads_bp", __name__)


@uploads_bp.route("/event/<int:event_id>/files", methods=["POST"])
def upload_event_files(event_id):
    event = Event.query.get_or_404(event_id)
    files = request.files.getlist("files")
    if not files:
        return jsonify({"success": False, "error": "לא נבחרו קבצים"}), 400

    upload_root = Path(current_app.config["UPLOAD_FOLDER"])
    event_dir = upload_root / f"event_{event.id}"
    event_dir.mkdir(parents=True, exist_ok=True)

    saved_items = []
    for f in files:
        filename = secure_filename(f.filename)
        if not filename:
            continue
        dest = event_dir / filename
        f.save(dest)

        mf = MediaFile(
            event=event,
            file_type="auto",
            path=str(dest),
            label=filename,
        )
        db.session.add(mf)
        saved_items.append({"filename": filename})

    db.session.commit()

    return jsonify({"success": True, "files": saved_items}), 201
