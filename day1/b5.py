# Bài 5: Merge two lists
# Yêu cầu: Ghép hai danh sách lại theo thứ tự từ bé đến lớn

from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def mergeTwoLists(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    if not list1 or not list2:
        return list1 or list2
    if list1.val < list2.val:
        list1.next = mergeTwoLists(list1.next, list2)
        return list1
    else:
        list2.next = mergeTwoLists(list1, list2.next)
        return list2

l1 = ListNode(1, ListNode(2, ListNode(4)))
l2 = ListNode(1, ListNode(3, ListNode(6)))
result = mergeTwoLists(l1, l2)

# In kết quả
print("Ket qua:")
while result:
    print(result.val, end=" -> ")
    result = result.next