CREATE TABLE audit_table (
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

CREATE TABLE taxa_desocupacao_semana_referente_14_anos_ou_mais(
    id_sexo integer,
    id_localidade integer,
    periodo varchar,
    taxa float,
    constraint super_key primary key (id_sexo, id_localidade, periodo)
) INHERITS (audit_table);

CREATE OR REPLACE TRIGGER audit_table_trigger
    BEFORE INSERT ON public.taxa_desocupacao_semana_referente_14_anos_ou_mais
    FOR EACH ROW EXECUTE PROCEDURE audit_table_function();


CREATE USER ibge_api WITH PASSWORD 'IBGE_API_123456';
GRANT INSERT ON taxa_desocupacao_semana_referente_14_anos_ou_mais TO ibge_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ibge_api;