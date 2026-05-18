from app.routes import chat, docx, files, memory, mock_pipeline, projects, reviews, templates

routers = [
    projects.router,
    files.router,
    mock_pipeline.router,
    chat.router,
    memory.router,
    reviews.router,
    docx.router,
    templates.router,
]
