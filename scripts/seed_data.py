import sys
from pathlib import Path

# Setup Path to import from scripts
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager
from scripts.models import Question, AnswerStep
from scripts.manage import save_changes

def seed():
    print("Seeding Database with Fresh Typst Content...")
    db = DBManager(PROJECT_ROOT / "data")

    new_questions = [
        # 1. Calculus (Integration)
        Question(
            id="qn-calc-integral",
            year=2024,
            lecturer="Prof. Gauss",
            topic="Calculus",
            given="Let $f(x) = x^2 e^x$.",
            to_prove="Calculate $integral_0^1 f(x) dif x$.",
            hint="Use integration by parts twice.",
            answer_steps=[
                AnswerStep(type="Calculation", title="Step 1", content="Let $u = x^2$ and $dif v = e^x dif x$."),
                AnswerStep(type="Result", title="Final Answer", content="$e - 2$.")
            ]
        ),
        # 2. Set Theory (De Morgan)
        Question(
            id="qn-set-demorgan",
            year=2023,
            lecturer="Dr. Cantor",
            topic="Set Theory",
            given="Let $A$ and $B$ be subsets of a universal set $U$.",
            to_prove="Prove $(A union B)^c = A^c sect B^c$.",
            hint="Show mutual inclusion (LHS subset RHS and RHS subset LHS).",
            answer_steps=[
                AnswerStep(type="Proof", title="Forward Direction", content="Let $x in (A union B)^c$. Then $x in.not A union B$.")
            ]
        ),
        # 3. Linear Algebra (Eigenvalues)
        Question(
            id="qn-linalg-eigen",
            year=2025,
            lecturer="Prof. Noether",
            topic="Linear Algebra",
            given="Let $A = mat(2, 1; 1, 2)$.",
            to_prove="Find the eigenvalues of $A$.",
            hint="Solve $det(A - lambda I) = 0$.",
            answer_steps=[
                AnswerStep(type="Calculation", title="Characteristic Eq", content="$(2-lambda)^2 - 1 = 0$.")
            ]
        ),
        # 4. Limits (Squeeze Theorem)
        Question(
            id="qn-limit-squeeze",
            year=2022,
            lecturer="Dr. Smith",
            topic="Limits",
            given="Let $x_n = (sin(n))/n$.",
            to_prove="Prove that $lim(x_n) = 0$.",
            hint="Use the Squeeze Theorem with $-1/n <= x_n <= 1/n$.",
            answer_steps=[
                AnswerStep(type="Proof", title="Bound", content="Since $|sin(n)| <= 1$, we have $-1 <= sin(n) <= 1$.")
            ]
        ),
        # 5. Complex Numbers (Roots)
        Question(
            id="qn-complex-roots",
            year=2024,
            lecturer="Prof. Euler",
            topic="Complex Analysis",
            given="Consider $z^3 = 1$.",
            to_prove="Find all roots of unity in the form $a + b i$.",
            hint="Use De Moivre's Theorem: $e^(i theta) = cos(theta) + i sin(theta)$.",
            answer_steps=[
                AnswerStep(type="Result", title="Roots", content="$1, (-1 + i sqrt(3))/2, (-1 - i sqrt(3))/2$.")
            ]
        ),
        # 6. Series (Convergence)
        Question(
            id="qn-series-ratio",
            year=2023,
            lecturer="Dr. Cauchy",
            topic="Series",
            given="Let $S = sum_(n=1)^infinity (n!)/(n^n)$.",
            to_prove="Determine if $S$ converges.",
            hint="Use the Ratio Test.",
            answer_steps=[
                AnswerStep(type="Calculation", title="Ratio", content="$lim_(n->infinity) |a_(n+1)/a_n| = 1/e < 1$.")
            ]
        ),
        # 7. Logic (Truth Table)
        Question(
            id="qn-logic-imply",
            year=2025,
            lecturer="Dr. Boole",
            topic="Logic",
            given="Propositions $P$ and $Q$.",
            to_prove="Show that $P => Q$ is equivalent to $not Q => not P$.",
            hint="Construct a truth table.",
            answer_steps=[
                AnswerStep(type="Proof", title="Contrapositive", content="This is the Law of Contrapositive.")
            ]
        ),
        # 8. Geometry (Vectors)
        Question(
            id="qn-vec-dot",
            year=2024,
            lecturer="Prof. Euclid",
            topic="Geometry",
            given="Vectors $vec(u) = (1, 2)$ and $vec(v) = (3, -1)$.",
            to_prove="Calculate the angle between $vec(u)$ and $vec(v)$.",
            hint="Use $vec(u) dot vec(v) = |vec(u)| |vec(v)| cos(theta)$.",
            answer_steps=[
                AnswerStep(type="Calculation", title="Dot Product", content="$1(3) + 2(-1) = 1$.")
            ]
        ),
        # 9. Combinatorics (Binomial)
        Question(
            id="qn-comb-pascal",
            year=2023,
            lecturer="Dr. Pascal",
            topic="Combinatorics",
            given="Expression $(x+y)^4$.",
            to_prove="Expand using the Binomial Theorem.",
            hint="Coefficients are 1, 4, 6, 4, 1.",
            answer_steps=[
                AnswerStep(type="Result", title="Expansion", content="$x^4 + 4x^3 y + 6x^2 y^2 + 4x y^3 + y^4$.")
            ]
        ),
        # 10. Topology (Open Sets)
        Question(
            id="qn-top-open",
            year=2025,
            lecturer="Prof. Haus",
            topic="Topology",
            given="Let $X = RR$ with standard topology.",
            to_prove="Prove that $(0, 1)$ is an open set.",
            hint="Find a ball $B_epsilon(x)$ for every point.",
            answer_steps=[
                AnswerStep(type="Proof", title="Radius", content="For any $x$, choose $epsilon = min(x, 1-x)$.")
            ]
        ),
    ]

    added_count = 0
    for q in new_questions:
        if q.id not in db.questions:
            db.add_node(q)
            added_count += 1
        else:
            print(f"   - Skipping {q.id} (already exists)")

    if added_count > 0:
        save_changes(db)
        print(f"Successfully added {added_count} new questions!")
    else:
        print("Database is already populated.")

if __name__ == "__main__":
    seed()
