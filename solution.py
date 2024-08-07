import numpy as np
import random
import subprocess


def generate_numbers(n, m):
    numbers = []
    for i in range(n):
        sequence = sorted([round(random.uniform(0, 1), 1) for _ in range(m)], reverse=True)
        numbers.extend(sequence)
    return numbers


def max_probability_allocation(n, m, probabilities):
    num_machines = m
    num_companies = n

    probabilities = np.array(probabilities).reshape(num_companies, num_machines)

    dp = np.zeros((num_companies + 1, num_machines + 1))
    dp[0, 0] = 1

    choices = [[[] for _ in range(num_machines + 1)] for _ in range(num_companies + 1)]

    for i in range(1, num_companies + 1):
        for j in range(num_machines + 1):
            for k in range(min(j, num_machines) + 1):  
                prob = dp[i - 1, j - k] * (probabilities[i - 1, k - 1] if k > 0 else 1)
                if prob > dp[i, j]:
                    dp[i, j] = prob
                    choices[i][j] = [[k]]
                elif prob == dp[i, j]:
                    choices[i][j].append([k])

    def get_all_allocations(i, j):
        if i == 0:
            return [[]]
        all_paths = []
        for choice in choices[i][j]:
            sub_paths = get_all_allocations(i - 1, j - choice[0])
            for sub_path in sub_paths:
                all_paths.append(sub_path + choice)
        return all_paths

    all_allocations = get_all_allocations(num_companies, num_machines)

    unique_allocations = []
    for alloc in all_allocations:
        if alloc not in unique_allocations:
            unique_allocations.append(alloc)

    solution_text = ""
    solution_text += "Матрица вероятностей:\n"
    solution_text += str(probabilities)
    solution_text += "\n\nОптимальные распределения машин по каждой компании (в порядке от первой до последней):\n"
    for alloc in unique_allocations:
        solution_text += str(alloc) + "\n"
    solution_text += f"\nМаксимальная вероятность выполнения заказа: {dp[num_companies, num_machines]:.5f}\n"

    return solution_text


def create_latex_table(numbers, n, m):
    latex = "\\begin{center}\n"
    latex += "\\begin{tabular}{|" + "c|" * (m + 1) + "}\n"
    latex += "\\hline\n"

    headers = " & " + " & ".join([str(i + 1) for i in range(m)]) + " \\\\ \\hline\n"
    latex += headers

    for i in range(n):
        row = " & ".join(map(str, numbers[i * m:(i + 1) * m])) + f" \\\\ \\hline\n"
        latex += f"$P_{{{i + 1}}}$ & " + row

    latex += "\\end{tabular}\n"
    latex += "\\end{center}\n"

    return latex


def create_latex_document(variants, solutions, n, m, with_solution=False):
    latex = "\\documentclass{article}\n"
    latex += "\\usepackage[utf8]{inputenc}\n"
    latex += "\\usepackage[russian]{babel}\n"
    latex += "\\usepackage{geometry}\n"
    latex += "\\usepackage{amsmath}\n"
    latex += "\\usepackage{graphicx}\n"
    latex += "\\geometry{a4paper, margin=1in}\n"
    latex += "\\begin{document}\n"

    for i, numbers in enumerate(variants):
        latex += f"\\section*{{Вариант № {i + 1}}}\n"
        latex += f"Срочный заказ по изготовлению {m} машин необходимо разместить между {n} предприятиями. "
        latex += f"Вероятности выполнения заказа $k$-ым предприятием равны $P_k$ (где $k$ - это индекс) зависят от величины заказа и заданы таблицей.\n"
        latex += create_latex_table(numbers, n, m)
        latex += f"\nНайти оптимальный план размещения заказа, при котором достигает максимум вероятность $P$ выполнения заказа всеми предприятиями.\n"
        if with_solution:
            latex += "\n\\textbf{Решение:}\n"
            latex += solutions[i].replace("\n", "\\newline\n")
        if i < len(variants) - 1:
            latex += "\\newpage\n"

    latex += "\\end{document}\n"

    return latex


def save_latex_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def compile_latex_to_pdf(latex_filename):
    result = subprocess.run(["pdflatex", latex_filename], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error during LaTeX compilation:")
        print(result.stderr)
        with open("error.log", 'w') as f:
            f.write(result.stderr)
    else:
        print("PDF file created successfully.")


n = 4  # number of rows (companies)
m = 5  # number of columns (machines)
M = 3  # number of variants

variants = [generate_numbers(n, m) for _ in range(M)]
solutions = [max_probability_allocation(n, m, variant) for variant in variants]

latex_content_without_solution = create_latex_document(variants, solutions, n, m, with_solution=False)
save_latex_file("tasks_only.tex", latex_content_without_solution)
compile_latex_to_pdf("tasks_only.tex")

latex_content_with_solution = create_latex_document(variants, solutions, n, m, with_solution=True)
save_latex_file("tasks_with_solutions.tex", latex_content_with_solution)
compile_latex_to_pdf("tasks_with_solutions.tex")
