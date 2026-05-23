from app.routes import chat, docx, files, llm, memory, mock_pipeline, projects, reviews, templates, thesis_docx

routers = [
    projects.router,
    files.router,
    mock_pipeline.router,
    chat.router,
    memory.router,
    llm.router,
    reviews.router,
    docx.router,
    templates.router,
    thesis_docx.router,
]
