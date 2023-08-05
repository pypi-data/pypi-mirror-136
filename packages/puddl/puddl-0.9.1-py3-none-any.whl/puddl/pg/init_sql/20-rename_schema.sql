DROP PROCEDURE IF EXISTS puddl_rename_schema(OLD TEXT, NEW TEXT)
;

CREATE PROCEDURE puddl_rename_schema(old TEXT, new TEXT)
    LANGUAGE plpgsql
AS
$$
DECLARE
    current_owner TEXT;
BEGIN
    SELECT schema_owner FROM information_schema.schemata WHERE schema_name = old INTO current_owner;
    -- become owner
    EXECUTE 'ALTER SCHEMA ' || old || ' OWNER TO puddl';
    EXECUTE 'ALTER SCHEMA ' || old || ' RENAME TO ' || new;
    EXECUTE 'ALTER SCHEMA ' || new || ' OWNER TO ' || current_owner;
    RAISE NOTICE 'renamed % to %', old, new;
END
$$
;

-- CALL puddl_rename_schema('log', 'oldlog')
