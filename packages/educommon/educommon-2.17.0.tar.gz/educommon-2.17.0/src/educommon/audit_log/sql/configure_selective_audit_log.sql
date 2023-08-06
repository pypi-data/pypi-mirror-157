DO
$do$
BEGIN
    IF EXISTS(SELECT * FROM pg_proc
              WHERE proname = 'set_for_selective_tables_triggers') THEN
        IF pg_try_advisory_lock({lock_id}) THEN
            PERFORM audit.set_for_selective_tables_triggers();
            PERFORM pg_advisory_unlock({lock_id});
        END IF;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        PERFORM pg_advisory_unlock({lock_id});
        RAISE;
END
$do$
LANGUAGE plpgsql;