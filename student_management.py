# ============================================================
#   Student Management System
#   Author  : Muhammad Ali  (BS-CS, 4th Year)
#   Version : 3.0
#   Date    : 2024
#   Desc    : A CLI-based student record manager with colors,
#             leaderboard, charts, badges, undo, backup & export.
# ============================================================

import os, json, csv, shutil, time
from datetime import datetime

# ── ANSI Colors ──────────────────────────────────────────────
class Color:
    RED    = "\033[91m";  GREEN  = "\033[92m";  YELLOW = "\033[93m"
    BLUE   = "\033[94m";  PINK   = "\033[95m";  CYAN   = "\033[96m"
    WHITE  = "\033[97m";  BOLD   = "\033[1m";   DIM    = "\033[2m"
    RESET  = "\033[0m";   GOLD   = "\033[38;5;220m"
    SILVER = "\033[38;5;250m";  BRONZE = "\033[38;5;172m"
    BG_DARK = "\033[48;5;235m"; UNDERLINE = "\033[4m"

def clr(col, txt): return f"{col}{txt}{Color.RESET}"
def bold(txt):     return f"{Color.BOLD}{txt}{Color.RESET}"
def dim(txt):      return f"{Color.DIM}{txt}{Color.RESET}"

# ── Config ───────────────────────────────────────────────────
DB_FILE    = "students.db"
BACKUP_DIR = "sms_backups"
PAGE_SIZE  = 6
VERSION    = "3.0"
AUTHOR     = "Muhammad Ali"

# ── Helpers ──────────────────────────────────────────────────
def clear(): os.system("cls" if os.name == "nt" else "clear")

def hr(char="─", width=60, color=Color.DIM):
    print(clr(color, char * width))

def pause():
    input(dim("\n  Press Enter to continue..."))

def grade(m):
    for limit, g in [(90,"A+"),(80,"A"),(70,"B"),(60,"C"),(50,"D")]:
        if m >= limit: return g
    return "F"

def grade_col(m):
    if m >= 80: return Color.GREEN
    if m >= 60: return Color.YELLOW
    if m >= 50: return Color.PINK
    return Color.RED

def pbar(m, w=22):
    f = int((m/100)*w)
    col = grade_col(m)
    return f"{col}{'█'*f}{'░'*(w-f)}{Color.RESET}"

def badges(s, all_s):
    b = []
    ml = [x["marks"] for x in all_s]
    avg = sum(ml)/len(ml) if ml else 0
    if s["marks"] == 100:        b.append(clr(Color.GOLD,   "💯 Perfect Score"))
    elif s["marks"] >= 90:       b.append(clr(Color.GOLD,   "🏆 Top Scorer"))
    if s["marks"] >= avg + 15:   b.append(clr(Color.CYAN,   "🌟 Outstanding"))
    if s["marks"] < 50:          b.append(clr(Color.RED,    "⚠  At Risk"))
    if len(s.get("subjects",{})): b.append(clr(Color.PINK,  "📖 Multi-Subject"))
    return "  ".join(b)

def fmt_time(): return datetime.now().strftime("%d %b %Y  %I:%M %p")

# ── Splash ───────────────────────────────────────────────────
def splash():
    clear()
    lines = [
        "",
        clr(Color.CYAN + Color.BOLD,
            "  ╔═══════════════════════════════════════════╗"),
        clr(Color.CYAN + Color.BOLD,
            "  ║                                           ║"),
        clr(Color.CYAN + Color.BOLD, "  ║") +
            clr(Color.YELLOW + Color.BOLD,
                "    📋  STUDENT MANAGEMENT SYSTEM         ") +
            clr(Color.CYAN + Color.BOLD, "║"),
        clr(Color.CYAN + Color.BOLD, "  ║") +
            clr(Color.DIM,
                f"         BS Computer Science · 4th Year    ") +
            clr(Color.CYAN + Color.BOLD, "║"),
        clr(Color.CYAN + Color.BOLD, "  ║") +
            clr(Color.DIM,
                f"         v{VERSION}  ·  Built by {AUTHOR}       ") +
            clr(Color.CYAN + Color.BOLD, "║"),
        clr(Color.CYAN + Color.BOLD,
            "  ║                                           ║"),
        clr(Color.CYAN + Color.BOLD,
            "  ╚═══════════════════════════════════════════╝"),
        "",
    ]
    for line in lines:
        print(line)
        time.sleep(0.06)

    feats = ["⚡ Fast CLI Interface", "🎨 Color-Coded Output",
             "📊 Visual Charts", "🏆 Live Leaderboard",
             "💾 Auto-Save & Backup", "📤 CSV / JSON Export"]
    print(clr(Color.DIM, "  ┌─ Features "), end="")
    for f in feats:
        print(clr(Color.DIM, f"· {f} "), end="", flush=True)
        time.sleep(0.05)
    print()
    print()
    input(clr(Color.CYAN, "  ▶  Press Enter to launch..."))

# ── Database ─────────────────────────────────────────────────
def load():
    data = []
    if not os.path.exists(DB_FILE): return data
    with open(DB_FILE) as f:
        for ln in f:
            ln = ln.strip()
            if not ln: continue
            parts = ln.split(",", 3)
            if len(parts) < 3: continue
            data.append({
                "name":     parts[0].strip(),
                "roll":     int(parts[1].strip()),
                "marks":    float(parts[2].strip()),
                "subjects": json.loads(parts[3]) if len(parts)==4 else {}
            })
    return data

def save(data, quiet=False):
    with open(DB_FILE, "w") as f:
        for s in data:
            f.write(f"{s['name']},{s['roll']},{s['marks']},"
                    f"{json.dumps(s.get('subjects',{}))}\n")
    if not quiet:
        print(clr(Color.GREEN, "\n  ✔  Saved successfully."))

def backup(data):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    save(data, quiet=True)
    ts   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest = os.path.join(BACKUP_DIR, f"backup_{ts}.db")
    shutil.copy(DB_FILE, dest)
    print(clr(Color.DIM, f"  📦 Backup created → {dest}"))

# ── Header bar ───────────────────────────────────────────────
def header(title):
    clear()
    print()
    print(clr(Color.CYAN + Color.BOLD,
        f"  ╔{'═'*56}╗"))
    print(clr(Color.CYAN + Color.BOLD, f"  ║") +
          clr(Color.YELLOW + Color.BOLD, f"  {title:<54}") +
          clr(Color.CYAN + Color.BOLD, "║"))
    print(clr(Color.CYAN + Color.BOLD,
        f"  ║") + clr(Color.DIM, f"  {fmt_time():<54}") +
          clr(Color.CYAN + Color.BOLD, "║"))
    print(clr(Color.CYAN + Color.BOLD,
        f"  ╚{'═'*56}╝"))
    print()

# ── Menu ─────────────────────────────────────────────────────
def menu(total):
    clear()
    print()
    W = 48
    top    = f"  ╔{'═'*W}╗"
    mid    = f"  ╠{'═'*W}╣"
    bot    = f"  ╚{'═'*W}╝"
    def row(n, ico, lbl, extra=""):
        line = f"  {bold(n)}  {ico}  {lbl}"
        if extra: line += clr(Color.DIM, f"  {extra}")
        pad = W - len(f"  {n}  {ico}  {lbl}{extra}") - 1
        return (clr(Color.CYAN+Color.BOLD,"  ║") +
                f"{line}" + " "*max(pad,1) +
                clr(Color.CYAN+Color.BOLD,"║"))

    print(clr(Color.CYAN+Color.BOLD, top))
    print(clr(Color.CYAN+Color.BOLD, "  ║") +
          clr(Color.YELLOW+Color.BOLD,
              f"   📋 Student Management System  v{VERSION}    ") +
          clr(Color.CYAN+Color.BOLD, "║"))
    print(clr(Color.CYAN+Color.BOLD, "  ║") +
          clr(Color.DIM,
              f"   {total} record(s) loaded  ·  {fmt_time()}   ") +
          clr(Color.CYAN+Color.BOLD, "║"))
    print(clr(Color.CYAN+Color.BOLD, mid))
    entries = [
        ("1","➕","Add Student",       ""),
        ("2","📋","View Records",       f"pg {PAGE_SIZE}/page"),
        ("3","✏️ ","Update Student",    ""),
        ("4","🗑 ","Delete Student",    ""),
        ("5","🔍","Search",             "name / roll"),
        ("6","📊","Stats + Chart",      ""),
        ("7","🏆","Leaderboard",        "ranked"),
        ("8","📤","Export",             "CSV · JSON"),
        ("9","↩️ ","Undo",              "last action"),
        ("B","📦","Backup",             "auto-timestamped"),
        ("S","💾","Save",               ""),
        ("X","🚪","Exit",               ""),
    ]
    for n,i,l,e in entries:
        print(row(n,i,l,e))
    print(clr(Color.CYAN+Color.BOLD, bot))
    print()
    return input(clr(Color.CYAN, "  ❯ Choice: ")).strip().upper()

# ── Add ──────────────────────────────────────────────────────
def add_student(data, undo):
    header("➕  Add New Student")

    name = input(clr(Color.CYAN,"  Full Name   : ")).strip()
    if not name:
        print(clr(Color.RED,"  ✘ Name cannot be empty.")); pause(); return

    while True:
        r = input(clr(Color.CYAN,"  Roll No.    : ")).strip()
        if r.isdigit(): roll = int(r); break
        print(clr(Color.RED,"  ✘ Must be a number."))

    if any(s["roll"]==roll for s in data):
        print(clr(Color.RED,f"  ✘ Roll {roll} already exists.")); pause(); return

    while True:
        m = input(clr(Color.CYAN,"  Marks (0-100): ")).strip()
        try:
            marks = float(m)
            if 0 <= marks <= 100: break
            print(clr(Color.YELLOW,"  ✘ Must be 0–100."))
        except: print(clr(Color.RED,"  ✘ Invalid number."))

    subjects = {}
    if input(clr(Color.DIM,"  Add subject-wise marks? (y/n): ")).strip().lower() == "y":
        print(clr(Color.DIM,"  (blank name = done)"))
        while True:
            sn = input(clr(Color.CYAN,"    Subject : ")).strip()
            if not sn: break
            while True:
                sv = input(clr(Color.CYAN,f"    {sn} marks: ")).strip()
                try:
                    v = float(sv)
                    if 0<=v<=100: subjects[sn]=v; break
                    print(clr(Color.YELLOW,"    Must be 0–100."))
                except: print(clr(Color.RED,"    Invalid."))

    student = {"name":name,"roll":roll,"marks":marks,"subjects":subjects}
    undo.append(("add", student))
    data.append(student)

    g   = grade(marks)
    col = grade_col(marks)
    b   = badges(student, data)
    print()
    hr("─", 50, Color.DIM)
    print(clr(Color.GREEN,f"  ✔  Added: {name}"))
    print(f"     Roll: {roll}  │  Marks: {clr(col,str(marks))}  │  Grade: {clr(col,g)}")
    print(f"     {pbar(marks)}  {marks}%")
    if b: print(f"     {b}")
    hr("─", 50, Color.DIM)
    pause()

# ── View ─────────────────────────────────────────────────────
def view_students(data):
    if not data:
        header("📋  Student Records")
        print(clr(Color.YELLOW,"  No records found.")); pause(); return

    total_pages = (len(data) + PAGE_SIZE - 1) // PAGE_SIZE
    page = 0

    while True:
        header(f"📋  Student Records  (Page {page+1}/{total_pages})")
        chunk = data[page*PAGE_SIZE : page*PAGE_SIZE+PAGE_SIZE]

        # Table header
        print(clr(Color.BOLD+Color.UNDERLINE,
            f"  {'#':<4} {'Name':<18} {'Roll':<7} {'Marks':<7} "
            f"{'Gr':<4} {'Progress Bar':<26} Badges"))
        print()

        for i, s in enumerate(chunk, page*PAGE_SIZE+1):
            col = grade_col(s["marks"])
            g   = grade(s["marks"])
            bar = pbar(s["marks"], 18)
            b   = badges(s, data)
            print(f"  {clr(Color.DIM,str(i)):<5}"
                  f"{bold(s['name']):<18}"
                  f"{clr(Color.DIM,str(s['roll'])):<7}"
                  f"{clr(col,str(s['marks'])):<7}"
                  f"{clr(col,g):<5}"
                  f"{bar}  {b}")
            if s.get("subjects"):
                sub = "  ".join(
                    f"{clr(Color.DIM,k)}: {clr(grade_col(v),str(v))}"
                    for k,v in s["subjects"].items()
                )
                print(f"  {'':4} └─ 📖 {sub}")
        print()
        hr()
        print(dim(f"  Total: {len(data)} students  ·  Page {page+1}/{total_pages}"))

        if total_pages == 1: pause(); break
        nav = input(clr(Color.CYAN,"  [n] Next  [p] Prev  [q] Back ❯ ")).strip().lower()
        if nav=="n" and page < total_pages-1: page += 1
        elif nav=="p" and page > 0:           page -= 1
        elif nav=="q":                         break

# ── Update ───────────────────────────────────────────────────
def update_student(data):
    header("✏️   Update Student")
    roll = input(clr(Color.CYAN,"  Enter Roll No.: ")).strip()
    if not roll.isdigit():
        print(clr(Color.RED,"  ✘ Invalid.")); pause(); return
    for s in data:
        if s["roll"]==int(roll):
            print(f"\n  Found: {bold(s['name'])}  │  Marks: {s['marks']}\n")
            nn = input(clr(Color.CYAN,f"  New name   [{s['name']}]  : ")).strip()
            nm = input(clr(Color.CYAN,f"  New marks  [{s['marks']}] : ")).strip()
            if nn: s["name"] = nn
            if nm:
                try:
                    v = float(nm)
                    if 0<=v<=100: s["marks"]=v
                    else: print(clr(Color.YELLOW,"  Marks out of range, skipped."))
                except: print(clr(Color.RED,"  Invalid marks, skipped."))
            print(clr(Color.GREEN,f"\n  ✔  Updated → {s['name']}  {s['marks']} marks"))
            pause(); return
    print(clr(Color.RED,f"  ✘ Roll {roll} not found.")); pause()

# ── Delete ───────────────────────────────────────────────────
def delete_student(data, undo):
    header("🗑   Delete Student")
    roll = input(clr(Color.CYAN,"  Enter Roll No.: ")).strip()
    if not roll.isdigit():
        print(clr(Color.RED,"  ✘ Invalid.")); pause(); return
    for i, s in enumerate(data):
        if s["roll"]==int(roll):
            print(f"\n  {bold(s['name'])}  │  Roll {s['roll']}  │  {s['marks']} marks")
            if input(clr(Color.YELLOW,"\n  Confirm delete? (yes/no): ")).strip().lower()=="yes":
                undo.append(("delete", (i, s)))
                data.pop(i)
                print(clr(Color.GREEN,"  ✔  Deleted."))
            else:
                print(dim("  Cancelled."))
            pause(); return
    print(clr(Color.RED,f"  ✘ Not found.")); pause()

# ── Undo ─────────────────────────────────────────────────────
def undo_last(data, undo):
    if not undo:
        print(clr(Color.YELLOW,"\n  Nothing to undo.")); pause(); return
    act, payload = undo.pop()
    if act=="add":
        data.remove(payload)
        print(clr(Color.GREEN,f"\n  ↩  Removed '{payload['name']}'."))
    elif act=="delete":
        idx, s = payload
        data.insert(idx, s)
        print(clr(Color.GREEN,f"\n  ↩  Restored '{s['name']}'."))
    pause()

# ── Search ───────────────────────────────────────────────────
def search(data):
    header("🔍  Search Student")
    q = input(clr(Color.CYAN,"  Name or Roll No.: ")).strip().lower()
    res = [s for s in data
           if q in s["name"].lower() or q==str(s["roll"])]
    if not res:
        print(clr(Color.RED,f"  ✘ Nothing found.")); pause(); return
    print(clr(Color.GREEN,f"\n  Found {len(res)} result(s):\n"))
    for s in res:
        col = grade_col(s["marks"])
        print(f"  {bold(s['name']):<20} Roll: {s['roll']:<6} "
              f"Marks: {clr(col,str(s['marks'])):<5} Grade: {clr(col,grade(s['marks']))}")
        print(f"  {pbar(s['marks'])}  {s['marks']}%")
        b = badges(s, data)
        if b: print(f"  {b}")
        print()
    pause()

# ── Stats ────────────────────────────────────────────────────
def stats_and_chart(data):
    header("📊  Class Statistics + Bar Chart")
    if not data:
        print(clr(Color.YELLOW,"  No data.")); pause(); return

    ml    = [s["marks"] for s in data]
    total = len(ml)
    avg   = sum(ml)/total
    hi    = max(ml); lo = min(ml)
    passd = sum(1 for m in ml if m>=50)
    faild = total - passd

    print(f"  {bold('Total Students')} : {total}")
    print(f"  {bold('Average Marks')}  : {clr(grade_col(avg), f'{avg:.1f}')}")
    print(f"  {bold('Highest')}        : {clr(Color.GREEN,str(hi))}  — "
          + ", ".join(s["name"] for s in data if s["marks"]==hi))
    print(f"  {bold('Lowest')}         : {clr(Color.RED,str(lo))}  — "
          + ", ".join(s["name"] for s in data if s["marks"]==lo))
    print(f"  {clr(Color.GREEN,'Passed')} : {passd}   "
          f"{clr(Color.RED,'Failed')} : {faild}")

    # Grade distribution
    print(f"\n  {bold('Grade Breakdown')}")
    hr("─", 40, Color.DIM)
    gcounts = {g:0 for g in ["A+","A","B","C","D","F"]}
    for s in data: gcounts[grade(s["marks"])] += 1
    PROXY = {"A+":95,"A":85,"B":75,"C":65,"D":55,"F":30}
    for g in ["A+","A","B","C","D","F"]:
        n   = gcounts[g]
        bar = "█" * n
        print(f"  {clr(grade_col(PROXY[g]), g):>6}  "
              f"{clr(grade_col(PROXY[g]), bar):<20} {n} student(s)")

    # Bar chart
    print(f"\n  {bold('Marks Bar Chart')}")
    hr("─", 58, Color.DIM)
    for s in data:
        name = s["name"][:15]
        print(f"  {name:<16} {pbar(s['marks'],28)}  {s['marks']:.0f}")

    # At-risk
    at_risk = [s for s in data if s["marks"]<50]
    if at_risk:
        print(f"\n  {clr(Color.RED+Color.BOLD, f'⚠  At-Risk Students ({len(at_risk)})')}")
        hr("─", 40, Color.RED)
        for s in at_risk:
            print(clr(Color.RED,
                f"  • {s['name']:<18} Roll {s['roll']:<5} {s['marks']} marks"))
    pause()

# ── Leaderboard ──────────────────────────────────────────────
def leaderboard(data):
    header("🏆  Leaderboard  — Top Rankings")
    if not data:
        print(clr(Color.YELLOW,"  No data.")); pause(); return

    ranked = sorted(data, key=lambda x: x["marks"], reverse=True)
    medals = {0:(Color.GOLD,"🥇 "),1:(Color.SILVER,"🥈 "),2:(Color.BRONZE,"🥉 ")}

    print(clr(Color.BOLD+Color.UNDERLINE,
        f"  {'Rank':<6} {'Name':<20} {'Roll':<7} {'Marks':<7} {'Grade':<5} Progress\n"))

    for i, s in enumerate(ranked):
        col, medal = medals.get(i, (Color.WHITE, f"  #{i+1} "))
        g = grade(s["marks"])
        print(f"  {clr(col, medal)}{clr(col+Color.BOLD, s['name']):<20} "
              f"{dim(str(s['roll'])):<7} "
              f"{clr(grade_col(s['marks']), str(s['marks'])):<7} "
              f"{clr(grade_col(s['marks']), g):<5} "
              f"{pbar(s['marks'], 18)}")
        b = badges(s, data)
        if b: print(f"  {'':7} {dim('└─')} {b}")

    avg = sum(s["marks"] for s in data)/len(data)
    print()
    hr("─", 58, Color.DIM)
    print(dim(f"  Class Average: {avg:.1f}  ·  {len(ranked)} students ranked"))
    pause()

# ── Export ───────────────────────────────────────────────────
def export(data):
    header("📤  Export Data")
    print("  1.  CSV  (open in Excel)")
    print("  2.  JSON (structured data)")
    print()
    ch = input(clr(Color.CYAN,"  Format (1/2): ")).strip()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if ch == "1":
        fn = f"students_{ts}.csv"
        with open(fn, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Name","Roll","Marks","Grade","Subjects"])
            for s in data:
                w.writerow([s["name"],s["roll"],s["marks"],
                             grade(s["marks"]),
                             json.dumps(s.get("subjects",{}))])
        print(clr(Color.GREEN, f"\n  ✔  Exported → {fn}"))

    elif ch == "2":
        fn = f"students_{ts}.json"
        out = [{**s, "grade": grade(s["marks"])} for s in data]
        with open(fn, "w") as f:
            json.dump(out, f, indent=2)
        print(clr(Color.GREEN, f"\n  ✔  Exported → {fn}"))
    else:
        print(clr(Color.RED,"  ✘ Invalid."))
    pause()

# ── Main Loop ────────────────────────────────────────────────
def main():
    splash()
    data = load()
    undo = []

    if data:
        print(clr(Color.GREEN,
            f"\n  ✔  Loaded {len(data)} record(s) from database."))
    else:
        print(dim("\n  No records found. Starting fresh."))
    time.sleep(0.8)

    while True:
        ch = menu(len(data))

        if   ch == "1": add_student(data, undo)
        elif ch == "2": view_students(data)
        elif ch == "3": update_student(data)
        elif ch == "4": delete_student(data, undo)
        elif ch == "5": search(data)
        elif ch == "6": stats_and_chart(data)
        elif ch == "7": leaderboard(data)
        elif ch == "8": export(data)
        elif ch == "9": undo_last(data, undo)
        elif ch == "B": backup(data)
        elif ch == "S": save(data)
        elif ch == "X":
            save(data, quiet=True)
            backup(data)
            clear()
            print()
            print(clr(Color.CYAN+Color.BOLD,
                "  ╔══════════════════════════════════╗"))
            print(clr(Color.CYAN+Color.BOLD, "  ║") +
                  clr(Color.YELLOW+Color.BOLD,
                      "   👋  Goodbye! Data saved.         ") +
                  clr(Color.CYAN+Color.BOLD, "║"))
            print(clr(Color.CYAN+Color.BOLD, "  ║") +
                  dim(f"   v{VERSION}  ·  {AUTHOR:<28}") +
                  clr(Color.CYAN+Color.BOLD, "║"))
            print(clr(Color.CYAN+Color.BOLD,
                "  ╚══════════════════════════════════╝\n"))
            break
        else:
            print(clr(Color.RED,"\n  ✘ Invalid choice."))
            time.sleep(0.6)

if __name__ == "__main__":
    main()
