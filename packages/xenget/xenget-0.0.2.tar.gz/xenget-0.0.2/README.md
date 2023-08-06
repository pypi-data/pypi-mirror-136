# XenGet
A library for Python to get information from a XenForo forum.

## Usage
Installation:
```sh
pip install xenget
```

### Documentation
This documentation is temporary, and will be moved to a better place soon.

```py
import xenget
```

#### Forum
Returns a Forum class. Usage:
```py
forum = xenget.Forum("https://yourforum.com")
```

##### Forum.get_member(id)
Returns a Member class. Usage:
```py
member = forum.get_member(12345)
```

##### Member
###### Member.get_avatar()
Returns an image. Usage:
```py
member = member.get_avatar()
```

###### Member.get_banner()
Returns an image. Usage:
```py
member = member.get_banner()
```

###### Member.get_username()
Returns a string. Usage:
```py
member = member.get_username()
```

###### Member.get_joindate()
Returns a string. Usage:
```py
member = member.get_joindate()
```