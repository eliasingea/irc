                                  Table "public.messages"
  Column  |          Type          |                       Modifiers                       
----------+------------------------+-------------------------------------------------------
 id       | integer                | not null default nextval('messages_id_seq'::regclass)
 username | character varying(12)  | not null
 message  | character varying(150) | not null
 room     | integer                | not null default 0
Indexes:
    "messages_pkey" PRIMARY KEY, btree (id)

