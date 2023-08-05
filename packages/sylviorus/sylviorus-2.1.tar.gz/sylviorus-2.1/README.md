# Installation Requirements
```
pip install sylviorus
```

# How to use


```
from sylviorus import SYL

x = SYL()

syl = x.get_info(user.id)
print(x)
print(x.reason)

```


# How to add Auto ban Code?

Add This Code on Your Gban Module check_and_ban

```
    x = SYL()
    syl = x.get_info(int(user.id))
    
    if not syl['blacklisted']:
            return        
    else:
                chat.kick_member(user_id)
                reason , enf , user = syl['reason'] , syl['enforcer'] , syl['user']
                print(reason)
 ```
 
 #Show User is Banned or not in user information
 
 ```
 try:
        x = SYL()
        syl = x.get_info(int(user.id))
        if not syl['blacklisted']:
                pass
        else:
                 
                if syl:
                    print(syl.reason)
        
    except:
        pass  # don't crash if api is down :)          

```
