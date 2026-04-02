# Bìa 1: Length of the Last Word
# Yêu cầu: Tính độ dài của chữ cuối trong câu
def lengthOfLastWord(s: str) -> int:
    words = s.split()
    last_word = words[-1]
    
    return len(last_word)

if __name__ == "__main__":
    string = "Hello World"
    result = lengthOfLastWord(string)
    print(f" Do dai tu cuoi cung: {result}")