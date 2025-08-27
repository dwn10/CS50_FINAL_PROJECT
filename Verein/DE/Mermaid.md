```mermaid
graph TD
    subgraph "Phase 1: Planung und Gründung"
        A1[Konzept definieren: Mission & Name] --> A2[Gründergruppe zusammenstellen (min. 7)];
        A2 --> A3[Satzung verfassen];
        A3 --> A4[Gründungsversammlung abhalten];
        A4 --> A5[Vorstand wählen];
    end

    subgraph "Phase 2: Registrierung und Formalisierung"
        B1[Termin beim Notar zur Beglaubigung] --> B2[Ins Vereinsregister eintragen (Amtsgericht)];
        B2 --> B3["e.V."-Status erhalten];
        B3 --> B4[Gemeinnützigkeit beantragen (Finanzamt)];
        B4 --> B5[Bankkonto für den Verein eröffnen];
    end

    subgraph "Phase 3: Betrieb"
        C1[Verwaltung: Beiträge & Buchführung] --> C2[Marketing: Web, Social Media, Mitgliederwerbung];
        C2 --> C3[Aktivitäten planen: Ausstellungen, Workshops];
        C3 --> C4[Fördermittel & Sponsoren suchen];
        C1 --> C5[Pflichten erfüllen: Steuern & DSGVO];
    end

    %% Verbindungen zwischen den Phasen
    A5 --> B1;
    B5 --> C1;

    %% Stile für einzelne Knoten zur besseren Kompatibilität
    style A1 fill:#E0F7FA,stroke:#00796B,stroke-width:2px
    style A2 fill:#E0F7FA,stroke:#00796B,stroke-width:2px
    style A3 fill:#E0F7FA,stroke:#00796B,stroke-width:2px
    style A4 fill:#E0F7FA,stroke:#00796B,stroke-width:2px
    style A5 fill:#E0F7FA,stroke:#00796B,stroke-width:2px
    
    style B1 fill:#FFF9C4,stroke:#FBC02D,stroke-width:2px
    style B2 fill:#FFF9C4,stroke:#FBC02D,stroke-width:2px
    style B3 fill:#FFF9C4,stroke:#FBC02D,stroke-width:2px
    style B4 fill:#FFF9C4,stroke:#FBC02D,stroke-width:2px
    style B5 fill:#FFF9C4,stroke:#FBC02D,stroke-width:2px

    style C1 fill:#FCE4EC,stroke:#D81B60,stroke-width:2px
    style C2 fill:#FCE4EC,stroke:#D81B60,stroke-width:2px
    style C3 fill:#FCE4EC,stroke:#D81B60,stroke-width:2px
    style C4 fill:#FCE4EC,stroke:#D81B60,stroke-width:2px
    style C5 fill:#FCE4EC,stroke:#D81B60,stroke-width:2px
```