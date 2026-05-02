# Diagrams — FreelanceMarketPlace

This folder contains the source and rendered diagrams referenced by the two academic
documents (`FreelanceMarketPlace_Final.doc` and `FreelanceMarketPlace_Project_Documentation.doc`).

## Folder Layout

```
diagrams/
├── drawio/       # draw.io source files (.drawio) — editable
├── images/       # PNG/SVG exports used by the .doc files
└── README.md
```

## Editing with draw.io

1. Open https://app.diagrams.net/ (or the desktop app).
2. File → Open → select any `.drawio` file in `drawio/`.
3. Edit the diagram.
4. Export as PNG: **File → Export as → PNG…**
   - Zoom: 200%
   - Transparent background: off
   - Border width: 10
5. Save the PNG to `images/` with the same base filename (e.g. `system_architecture.drawio` → `system_architecture.png`).

The `.doc` files reference relative paths `diagrams/images/<name>.png`, so keep the folder structure intact.

## Self-Contained Rendering

Both `.doc` files also include **inline SVG** fallbacks of every diagram, so they render
correctly in Microsoft Word / LibreOffice even if the PNG exports have not yet been generated.
Regenerate PNGs only if you need higher-resolution print output.

## Diagram Inventory

| # | File (base name)              | Type                       | Used in |
|---|-------------------------------|----------------------------|---------|
| 1 | `system_architecture`         | 3-tier deployment          | Final, Tech |
| 2 | `dfd_level0`                  | Context DFD (Level 0)      | Final |
| 3 | `dfd_level1`                  | Level-1 DFD                | Final |
| 4 | `er_diagram`                  | Entity-Relationship        | Final, Tech |
| 5 | `project_state_machine`       | Project lifecycle states   | Final, Tech |
| 6 | `contract_workflow`           | Proposal → Contract flow   | Final |
| 7 | `escrow_payment_flow`         | Escrow & milestone payouts | Final, Tech |
| 8 | `auth_flow`                   | Registration / Login       | Tech |
| 9 | `messaging_flow`              | Conversation & polling     | Tech |
| 10| `notification_flow`           | Event → Notification       | Tech |

## Test Login Credentials

The following pre-seeded accounts are available in the development database for
demos and walk-throughs of each role's flow. **Do not use these credentials in
production.**

> Login is performed with the **email address** (not the username). The login
> form is at `/accounts/login/`.

| Role        | Login (email)            | Password        | Username (informational) | After login lands on |
|-------------|--------------------------|-----------------|--------------------------|----------------------|
| Admin       | `admin@example.com`      | `admin123`      | `admin`                  | `/admin-panel/` (admin dashboard) |
| Freelancer  | `freelancer@example.com` | `freelancer123` | `samplefreelancer`       | `/dashboard/` (freelancer dashboard) |
| Client      | `client@example.com`     | `client123`     | `sampleclient`           | `/dashboard/` (client dashboard) |

**Sample profile data on the seeded accounts:**

- *Freelancer (Sam Freelancer)* — Title: *Full Stack Developer*, Category: *Health Care*,
  Hourly rate: $45/hr, Skills: *Python, Django, JavaScript*, Availability: Available.
- *Client (Chris Client / Acme Corp)* — Industry: *Technology*, Company size: *11–50*.
- *Admin* — Django superuser account; can also access the standard Django admin at `/admin/`.

### Re-seeding the test users

If the database is wiped, the same three accounts can be recreated with:

```powershell
python manage.py shell -c "
from apps.accounts.models import User, FreelancerProfile, ClientProfile
from apps.projects.models import Category
cat = Category.objects.filter(is_active=True).first()

f, _ = User.objects.get_or_create(email='freelancer@example.com', defaults={'username':'samplefreelancer','role':'freelancer','first_name':'Sam','last_name':'Freelancer','is_profile_complete':True})
f.set_password('freelancer123'); f.role='freelancer'; f.is_profile_complete=True; f.save()
fp, _ = FreelancerProfile.objects.get_or_create(user=f)
fp.title='Full Stack Developer'; fp.bio='Sample freelancer for testing the marketplace.'
fp.hourly_rate=45; fp.experience_years=4; fp.skills=['Python','Django','JavaScript']
fp.availability='available'
if cat: fp.category=cat
fp.save()

c, _ = User.objects.get_or_create(email='client@example.com', defaults={'username':'sampleclient','role':'client','first_name':'Chris','last_name':'Client','is_profile_complete':True})
c.set_password('client123'); c.role='client'; c.is_profile_complete=True; c.save()
cp, _ = ClientProfile.objects.get_or_create(user=c)
cp.company_name='Acme Corp'; cp.industry='Technology'; cp.company_size='11-50'
cp.save()
"
```

The admin user can be (re-)created with `python manage.py createsuperuser`.
