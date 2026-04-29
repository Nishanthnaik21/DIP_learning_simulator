import os, glob

backend_dir = r'c:\Users\Nishanth Naik\Desktop\dip_simulator_v4\backend'

# Process app.py
app_py_path = os.path.join(backend_dir, 'app.py')
with open(app_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
skip = False
for line in lines:
    if '# ── Auth guard' in line:
        skip = True
    elif skip and line.startswith('# ── Theme injection'):
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

final_lines = []
skip = False
for line in new_lines:
    if 'if st.button("🚪 Log Out"' in line:
        skip = True
    elif skip and 'theme_toggle_button()' in line:
        skip = False
        final_lines.append(line)
    elif skip and not line.strip():
        continue
    elif skip and 'st.switch_page' in line:
        continue
    elif skip and 'st.session_state.clear()' in line:
        continue
    elif not skip:
        final_lines.append(line)

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))
print('Updated app.py')

# Process all pages
pages_dir = os.path.join(backend_dir, 'pages')
for py_file in glob.glob(os.path.join(pages_dir, '*.py')):
    if '0_Login.py' in py_file:
        os.remove(py_file)
        print('Deleted 0_Login.py')
        continue

    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if '# ── Auth guard' in line:
            skip = True
        elif skip and line.startswith('del _st_g'):
            skip = False
        elif not skip:
            new_lines.append(line)

    with open(py_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print(f'Updated {os.path.basename(py_file)}')
