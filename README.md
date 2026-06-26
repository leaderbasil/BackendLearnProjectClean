[ Client / Postman ]
       │
       │ (1) POST /blog (multipart/form-data: title, content, file)
       ▼
┌─────────────────────────────────────────────────────────────┐
│  MIDDLEWARE (main.py)                                       │
│  - Starts timer                                             │
│  - Passes request to Router                                │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  ROUTER LAYER (blog_router.py)                             │
│  - Extracts: title=Form(...), content=Form(...), file=File()│
│  - Validates user token via Dependency (get_current_user)  │
│  - Calls: BlogService.create_blog(...)                     │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  SERVICE LAYER (blog_service.py)                           │
│  - Validates business rules (e.g., is user active?)        │
│  - Reads file bytes into memory                            │
│  - Calls: ImageKitUploader.upload(file) ──────────────┐    │
└─────────────────────────────────────────────────────────────┘
       │                                                  │
       │ <──────────────── Returns Image URL ────────────┘
       ▼
┌─────────────────────────────────────────────────────────────┐
│  EXTERNAL API (core/imagekit_upload.py)                   │
│  - Sends raw bytes via HTTP POST to ImageKit API          │
│  - Returns the hosted CDN URL (e.g., https://ik.image...) │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  REPOSITORY LAYER (blog_repository.py)                    │
│  - Receives: title, content, file_url, owner_id           │
│  - Executes: db.add(blog) & db.flush()                    │
│  - Returns the ORM Blog object                            │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  MIDDLEWARE (main.py)                                       │
│  - Stops timer                                             │
│  - Logs: POST /blog → 201 [0.450s]                        │
│  - Returns HTTP Response to Client                         │
└─────────────────────────────────────────────────────────────┘
