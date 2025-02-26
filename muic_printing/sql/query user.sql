select usr.user_name,
       usr.full_name,
       account.balance,
       usr.email,
       usr.department,
       usr.office,
       usr.card_number,
       usr.card_number2,
       usr.disabled_printing,
       usr.home_directory,
       usr.notes
from tbl_user usr
left join (
    select * from tbl_account  where deleted = 'N'
) account on usr.user_name = account.account_name
where usr.deleted = 'N'
order by usr.department,usr.office