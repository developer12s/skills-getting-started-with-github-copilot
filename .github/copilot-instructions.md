# GitHub Copilot Instructions for Mergington High School Activities API

## Project Overview

This is a simple but complete **FastAPI + Vanilla JavaScript** application for managing student extracurricular activities. It's designed as an educational project to demonstrate Copilot skills.

**Architecture**: 
- **Backend**: FastAPI server (`src/app.py`) with in-memory activity database
- **Frontend**: Single-page HTML/CSS/JS (`src/static/`) with no build tools
- **Data**: In-memory dictionary structure - resets on server restart

## Running the Project

```bash
# Install dependencies (FastAPI + Uvicorn)
pip install -r requirements.txt

# Run the server (auto-reloads on file changes)
cd src && python app.py

# Or with explicit port binding
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server runs on `http://localhost:8000` with auto-reload enabled.

## Key Patterns & Conventions

### Backend Data Model
- **Activities dictionary**: Maps activity name (string) → details dict
  - Keys: `description`, `schedule`, `max_participants`, `participants` (email list)
  - Used directly; no ORM or schema validation
- No database - all data volatile; design for statelessness and testability

### API Design
- **Endpoints**: `/activities` (GET) and `/activities/{activity_name}/signup` (POST)
- **Error handling**: Uses FastAPI's `HTTPException(status_code=404)` for not found
- **Query parameters**: Email passed as query string in signup endpoint
- **No request body**: Keep endpoint signatures simple

### Frontend Patterns
- **Single HTML file** (`index.html`) loads CSS and JavaScript statically
- **DOM queries with IDs**: Use `getElementById()` for predictable access
- **Async/await fetch()**: All API calls use fetch with try-catch
- **Event listeners**: Attach to `DOMContentLoaded` (wait for DOM ready)
- **URL encoding**: Use `encodeURIComponent()` for activity names in URLs

### Style Conventions
- **CSS classes**: Use lowercase with hyphens (e.g., `activity-card`, `form-group`)
- **JavaScript naming**: camelCase for functions/variables
- **Responsive design**: Single stylesheet `styles.css` handles layout

## Integration Points

1. **Static file mounting**: FastAPI mounts `/static` directory at root
   - Redirect `/` → `/static/index.html`
   - Serve CSS/JS from `src/static/`

2. **CORS**: Not currently implemented; same-origin only

3. **Frontend API calls**: Always use relative URLs (`/activities`, `/static/...`)

## Common Modifications

- **Add activity field**: Update dictionary keys in `activities` dict, then display in `app.js` card rendering
- **Add API endpoint**: Create new `@app.get()` or `@app.post()` function, test via Swagger UI at `/docs`
- **Modify UI**: Edit `index.html` structure, then update `app.js` selectors to match
- **Styling**: Add CSS classes in `styles.css` and apply to HTML elements

## Testing Notes

- **No test framework setup yet**: pytest available but tests not written
- **Manual testing**: Use Swagger UI (`/docs`) or curl for API testing
- **Browser DevTools**: Check console for JavaScript errors and network tab for API calls

## Common Pitfalls

- **Activity names are case-sensitive** in both API and frontend
- **URL encoding required**: Activity names with spaces need `encodeURIComponent()`
- **Participants list grows unbounded**: No duplicate checking or signup limits enforced
- **In-memory only**: Changes lost on server restart
