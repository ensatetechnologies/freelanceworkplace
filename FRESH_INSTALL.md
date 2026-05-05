# Fresh Install Guide (For a New Laptop)

This guide is for setting up the project from scratch on a different system after pulling the latest code from
[github.com/ensatetechnologies/freelanceworkplace](https://github.com/ensatetechnologies/freelanceworkplace).

## Why this guide exists

If the app was previously installed on the target laptop, the database schema may be out of sync with the current code.
A typical symptom is:

```
OperationalError at /accounts/signup/
(1054, "Unknown column 'freelancer_profiles.category_id' in 'field list'")
```

This means a new column (`category_id` on `freelancer_profiles`) was added to the model but the migration was never
applied on that laptop's MySQL database. The fix below wipes the old install (DB + venv) and rebuilds it cleanly.

The migration `apps/accounts/migrations/0003_freelancerprofile_category.py` IS in the repo, so a clean install + `migrate`
resolves the error.

---

## Prerequisites

- Python 3.11 or higher
- MySQL 8.0 (running locally)
- Git

Confirm versions:

```bash
python --version
mysql --version
git --version
```

---

## Step 1 — Get the latest code

If a previous copy exists, delete it (or clone into a new folder):

```bash
# Option A: pull latest into existing clone
cd path/to/freelanceworkplace
git fetch origin
git reset --hard origin/main

# Option B: fresh clone (recommended on a new laptop)
git clone https://github.com/ensatetechnologies/freelanceworkplace.git
cd freelanceworkplace
```

> If the previous setup was a downloaded ZIP (`freelanceworkplace-main(2).zip` etc.), delete that folder
> entirely and use a real `git clone` so future updates are easy.

---

## Step 2 — Remove the old database (clean slate)

This drops the old `freelance_marketplace` database, removing every stale table including the one that
caused the `category_id` error. Replace `<password>` with your MySQL root password.

Open the MySQL shell:

```bash
mysql -u root -p
```

Inside MySQL:

```sql
DROP DATABASE IF EXISTS freelance_marketplace;
CREATE DATABASE freelance_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

> If you cannot or do not want to drop the DB, you can instead just run `python manage.py migrate` — but a
> drop + recreate is the most reliable fix for an academic demo.

---

## Step 3 — Recreate the virtual environment

If a `venv/` folder already exists from a previous install, delete it:

```bash
# Windows
rmdir /s /q venv

# macOS / Linux
rm -rf venv
```

Create a new one:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> If `mysqlclient` fails to install on Windows, install the MySQL Connector C library or use
> `pip install mysqlclient --only-binary :all:`.

---

## Step 4 — Configure environment variables

Copy `env.example` to `.env`:

```bash
# Windows
copy env.example .env

# macOS / Linux
cp env.example .env
```

Edit `.env` and set `DB_PASSWORD` to your MySQL root password. Default contents:

```env
DEBUG=1
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=freelance_marketplace
DB_USER=root
DB_PASSWORD=<your-mysql-password>
DB_HOST=localhost
DB_PORT=3306
```

---

## Step 5 — Apply ALL migrations

This is the step that creates `freelancer_profiles.category_id` and every other table.

```bash
python manage.py migrate
```

Verify everything is applied (every entry should show `[X]`):

```bash
python manage.py showmigrations
```

In particular, the `accounts` app should show:

```
accounts
 [X] 0001_initial
 [X] 0002_alter_freelancerprofile_bio_and_more
 [X] 0003_freelancerprofile_category
```

If `0003_freelancerprofile_category` is `[ ]` (not applied), re-run `python manage.py migrate accounts`.

---

## Step 6 — Load seed data (categories, skills, site)

```bash
python manage.py loaddata fixtures/initial_data.json
```

This populates:

- `sites.site` row (so allauth works)
- 8 project categories (Web Dev, Mobile, Design, Writing, Marketing, Data Science, Video, Business)
- A starter set of skills

---

## Step 7 — Create an admin user

```bash
python manage.py createsuperuser
```

Provide an email, username, and password when prompted.

---

## Step 8 — Run the server

```bash
python manage.py runserver
```

Open in browser:

- Main site: <http://localhost:8000/>
- Sign up: <http://localhost:8000/accounts/signup/>
- Admin (Django built-in): <http://localhost:8000/admin/>
- Admin Dashboard (custom): <http://localhost:8000/dashboard/>

---

## Step 9 — Smoke test the signup flow

This is the exact path that broke before. After the steps above it should now succeed.

1. Open <http://localhost:8000/accounts/signup/>
2. Fill in: First name, Last name, Username, Email, Role = **Freelancer**, Password (twice)
3. Click **Sign Up**
4. Expected result: redirect to `/accounts/profile/setup/` with no `OperationalError`

Repeat with **Role = Client** to confirm both signup paths work.

---

## Troubleshooting

### `(1054, "Unknown column 'freelancer_profiles.category_id' ...")`
Migrations were not applied. Run `python manage.py migrate` (Step 5). If it still fails, drop the DB
(Step 2) and start over from Step 5.

### `django.db.utils.OperationalError: (2002, "Can't connect to MySQL server")`
MySQL service is not running. Start it (Windows: `net start mysql80`; macOS: `brew services start mysql`;
Linux: `sudo systemctl start mysql`).

### `Access denied for user 'root'@'localhost'`
Wrong password in `.env`. Update `DB_PASSWORD`.

### `ModuleNotFoundError: No module named 'MySQLdb'`
Activate the venv first, then `pip install mysqlclient`.

### `IntegrityError` during `loaddata`
A previous `loaddata` already inserted the rows. Drop and recreate the DB (Step 2), then re-run Steps 5–6.

### Want SQLite instead of MySQL (easier for demos)
Edit `config/settings/development.py` — comment out the `DATABASES` MySQL block and uncomment the SQLite
block at the bottom. Then run Steps 5–8 again (no DB drop needed; just delete `db.sqlite3` if it exists).

---

## One-shot reset script (Windows)

If you need to redo everything from scratch later:

```cmd
rmdir /s /q venv
mysql -u root -p -e "DROP DATABASE IF EXISTS freelance_marketplace; CREATE DATABASE freelance_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/initial_data.json
python manage.py createsuperuser
python manage.py runserver
```

## One-shot reset script (macOS / Linux)

```bash
rm -rf venv
mysql -u root -p -e "DROP DATABASE IF EXISTS freelance_marketplace; CREATE DATABASE freelance_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/initial_data.json
python manage.py createsuperuser
python manage.py runserver
```
