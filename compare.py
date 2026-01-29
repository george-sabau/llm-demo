file1 = "domain_corpus_v2_clean.txt"
file2 = "domain_corpus_candidates.csv"

def count_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

lines1 = count_lines(file1)
lines2 = count_lines(file2)

if lines1 == lines2:
    print(f"✅ Both files have the same number of lines: {lines1}")
else:
    print(f"❌ Different number of lines: {file1}={lines1}, {file2}={lines2}")