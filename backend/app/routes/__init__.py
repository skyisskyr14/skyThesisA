from app.routes import chat, docx, files, llm, memory, papers, projects, real_pipeline, reviews, templates, thesis_docx, versions

routers = [
    projects.router,
    files.router,
    papers.router,
    versions.router,
    chat.router,
    memory.router,
    llm.router,
    reviews.router,
    docx.router,
    templates.router,
    real_pipeline.router,
    thesis_docx.router,
]
