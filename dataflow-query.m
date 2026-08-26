let
    Source =
        Csv.Document(
            Web.Contents(
                "https://raw.githubusercontent.com",
                [
                    RelativePath =
                        "YOUR_GITHUB_USERNAME/wa-security-register/main/data/wa_security_officers.csv"
                ]
            ),
            [
                Delimiter = ",",
                Columns = 3,
                Encoding = 65001,
                QuoteStyle = QuoteStyle.Csv
            ]
        ),

    PromotedHeaders =
        Table.PromoteHeaders(
            Source,
            [PromoteAllScalars = true]
        ),

    ChangedTypes =
        Table.TransformColumnTypes(
            PromotedHeaders,
            {
                {"Licence Number", Int64.Type},
                {"Full Name", type text},
                {"Expiry Date", type date}
            }
        )
in
    ChangedTypes

