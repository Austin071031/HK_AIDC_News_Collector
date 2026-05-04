type ClusterDetailPageProps = {
  params: Promise<{
    clusterId: string;
  }>;
};

export default async function ClusterDetailPage({
  params,
}: ClusterDetailPageProps) {
  const { clusterId } = await params;

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "48px 24px",
        background: "#f3f7fb",
        color: "#08131a",
      }}
    >
      <div
        style={{
          maxWidth: "840px",
          margin: "0 auto",
          padding: "32px",
          borderRadius: "24px",
          background: "#ffffff",
          boxShadow: "0 24px 60px rgba(12, 36, 53, 0.12)",
        }}
      >
        <p
          style={{
            margin: 0,
            fontSize: "12px",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            color: "#547086",
          }}
        >
          Cluster Detail
        </p>
        <h1 style={{ margin: "12px 0 8px", fontSize: "36px" }}>{clusterId}</h1>
        <p style={{ margin: 0, color: "#607586" }}>
          Detailed cluster views will be connected to the backend in the next
          pipeline stage.
        </p>
      </div>
    </main>
  );
}
