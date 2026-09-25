import java.io.*;
import java.util.*;

public class FileStorage {
    public static void saveData(String filepath, Map<String, Transaction> transactions) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filepath))) {
            for (Transaction transaction : transactions.values()) {
                writer.write(transaction.toCSV());
                writer.newLine();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static Map<String, Transaction> loadData(String filepath) {
        Map<String, Transaction> transactions = new HashMap<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                Transaction transaction = Transaction.fromCSV(line);
                if (transaction != null) {
                    transactions.put(transaction.getTransactionId(), transaction);
                }
            }
        } catch (FileNotFoundException e) {
            // Ignore, return empty map
        } catch (IOException e) {
            e.printStackTrace();
        }
        return transactions;
    }
}