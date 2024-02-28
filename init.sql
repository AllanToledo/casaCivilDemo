CREATE TABLE IF NOT EXISTS audit_table (
    id bigserial primary key,
    username text,
    date_insert timestamp,
    ip_addr inet,
    ip_port integer
);

CREATE OR REPLACE FUNCTION audit_table_function() RETURNS trigger AS $$
BEGIN
    new.username := current_user;
    new.date_insert := now();
    new.ip_addr := inet_client_addr();
    new.ip_port := inet_client_port();
    RETURN new;
END
$$ LANGUAGE plpgsql;

--ano;valor;indicador_codigo;local_codigo;data;periodoDaFrequencia;frequencia

DROP TABLE indicadores;
CREATE TABLE indicadores(
    ano integer,
    valor float,
    indicador_codigo integer,
    local_codigo integer,
    periodo_da_frequencia integer,
    frequencia varchar(20),
    constraint super_key primary key (indicador_codigo, ano, periodo_da_frequencia, frequencia, local_codigo)
) INHERITS (audit_table);

CREATE OR REPLACE TRIGGER audit_table_trigger
    BEFORE INSERT ON public.indicadores
    FOR EACH ROW EXECUTE PROCEDURE audit_table_function();


CREATE USER ibge_api WITH PASSWORD 'IBGE_API_123456';
GRANT INSERT ON indicadores TO ibge_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ibge_api;