
graph TD
    subgraph Fase 1: Planificación y Fundación
        A1[Definir Concepto: Misión y Nombre] --> A2[Reunir Grupo Fundador (mín. 7)];
        A2 --> A3[Redactar Estatutos (Satzung)];
        A3 --> A4[Celebrar Reunión Fundacional];
        A4 --> A5[Elegir Junta Directiva (Vorstand)];
    end

    subgraph Fase 2: Registro y Formalización
        B1[Cita con Notario para certificar firmas] --> B2[Inscribir en el Registro de Asociaciones (Amtsgericht)];
        B2 --> B3[Obtener estatus "e.V."];
        B3 --> B4[Solicitar Utilidad Pública (Finanzamt)];
        B4 --> B5[Abrir Cuenta Bancaria del Verein];
    end

    subgraph Fase 3: Operaciones
        C1[Gestión Administrativa: Cuotas y Contabilidad] --> C2[Marketing: Web, Redes, Captación de Miembros];
        C2 --> C3[Planificar Actividades: Exposiciones, Talleres];
        C3 --> C4[Buscar Financiación: Subvenciones y Patrocinios];
        C1 --> C5[Cumplir Obligaciones: Impuestos y DSGVO];
    end

    A5 --> B1;
    B5 --> C1;

    style Fase1 fill:#E0F7FA,stroke:#00796B
    style Fase2 fill:#FFF9C4,stroke:#FBC02D
    style Fase3 fill:#FCE4EC,stroke:#D81B60
