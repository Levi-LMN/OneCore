mkdir -p templates/{sales,products,expenses,reports,admin,stock,errors} && \
touch templates/{base.html,login.html,dashboard.html} \
templates/sales/list.html \
templates/errors/{404.html,500.html} && \
echo "Template structure created successfully!

Directory structure:
templates/
├── base.html
├── login.html
├── dashboard.html
├── sales/
│   ├── list.html
│   └── new.html (create manually)
├── products/
│   ├── list.html (create manually)
│   ├── new.html (create manually)
│   └── variants.html (create manually)
├── expenses/
│   ├── list.html (create manually)
│   └── new.html (create manually)
├── reports/
│   ├── index.html (create manually)
│   └── daily.html (create manually)
├── admin/
│   ├── index.html (create manually)
│   ├── users.html (create manually)
│   ├── categories.html (create manually)
│   └── sizes.html (create manually)
├── stock/
│   └── management.html (create manually)
└── errors/
    ├── 404.html
    └── 500.html

Note: Due to length constraints, only key templates are included.
You'll need to create the remaining templates manually using the patterns shown."
