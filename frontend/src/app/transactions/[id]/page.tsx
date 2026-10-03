'use client';
export default function TransactionDetail({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Transaction {params.id}</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <p className="text-gray-600">Details for {params.id} would load here.</p>
      </div>
    </div>
  );
}
