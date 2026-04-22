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
